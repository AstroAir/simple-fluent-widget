# Fluent Widget Examples

This directory contains comprehensive usage examples for all components in the simple-fluent-widget library, organized by component category.

## Quick Start

To run any example, navigate to the project root and use:

```bash
python examples/<category>/<example_name>.py
```

For example:
```bash
python examples/layout/layout_components_demo.py
python examples/basic/forms/forms_demo.py
python examples/data/charts/data_charts_demo.py
```

## Overview

The examples demonstrate:
- Component configuration and customization
- Interactive features and user interactions
- Best practices and common usage patterns
- Theme integration and responsive design
- Error handling and fallback behaviors
- Real-time property adjustments and live demonstrations

## Example Categories

### 📐 Layout Components
**Directory:** `examples/layout/`

- **`layout_components_demo.py`** - Comprehensive layout system showcase
  - FluentStackPanel (vertical/horizontal stacking with interactive controls)
  - FluentScrollViewer (smooth scrolling containers)
  - FluentCard (elevated containers with shadows)
  - Grid layouts with responsive design
  - Layout combinations and best practices

- **`dock_panel_demo.py`** - Dockable panel layouts
  - Multi-panel arrangements with resizable areas
  - Panel docking and undocking functionality

### 🎯 Basic Components
**Directory:** `examples/basic/`

#### Forms (`examples/basic/forms/`)
- **`forms_demo.py`** - Form input components showcase
  - Text inputs, checkboxes, radio buttons
  - Dropdowns, sliders, number inputs
  - Form validation and real-time feedback
  - Interactive form builder with live preview

#### Display (`examples/basic/display/`)
- **`display_demo.py`** - Display and feedback components
  - Labels, badges, progress indicators
  - Status displays, notifications, alerts
  - Rich text and formatted content display

#### Navigation (`examples/basic/navigation/`)
- **`navigation_demo.py`** - Navigation components
  - Breadcrumbs, pagination controls
  - Navigation bars and tab controls
  - Step indicators and progress tracking

### 📊 Data Components
**Directory:** `examples/data/`

#### Input (`examples/data/input/`)
- **`data_input_demo.py`** - Advanced data entry components
  - Date/time pickers with calendar integration
  - File selectors and upload components
  - Rich text editors and code editors
  - Data validation and formatting

#### Display (`examples/data/display/`)
- **`data_display_demo.py`** - Data presentation components
  - Sortable and filterable data tables
  - Data cards, lists, and grid views
  - Search functionality and data exploration tools

#### Charts (`examples/data/charts/`)
- **`data_charts_demo.py`** - Data visualization showcase
  - Interactive charts and graphs (bar, line, pie, scatter)
  - Real-time data updates and animations
  - Chart customization and theming options

### 🏗️ Composite Components
**Directory:** `examples/composite/`

- **`composite_demo.py`** - Complex composite widgets
  - Multi-component forms with validation
  - Dashboard layouts with multiple panels
  - Settings panels with categorized sections

### 💬 Dialog Components
**Directory:** `examples/dialogs/`

- **`dialog_components_demo.py`** - Dialog system comprehensive showcase
  - Message dialogs (info, warning, error, success)
  - Confirmation dialogs with custom actions
  - Form dialogs with validation
  - Progress dialogs with cancellation
  - Teaching tips and contextual flyouts
  - Custom dialogs with animations

### 🎛️ Interface Components
**Directory:** `examples/interface/`

- **`interface_components_demo.py`** - Interface elements showcase
  - Command bars and toolbars with icons
  - Context menus and dropdown menus
  - Navigation views and pivot controls
  - Ribbon interfaces and command palettes
  - Menu bars with submenus and shortcuts

### 📺 Media Components
**Directory:** `examples/media/`

- **`media_controls_demo.py`** - Media and multimedia showcase
  - Audio/video players with standard controls
  - Image viewers and galleries with zoom
  - Streaming media controls and progress
  - Media metadata display and editing

### 🎮 Controls Components
**Directory:** `examples/controls/`

- **`controls_demo.py`** - Interactive controls showcase
  - Color pickers with palette and custom colors
  - Date/time pickers with various formats
  - File pickers and directory browsers
## Features Demonstrated

### 🎨 Theming and Styling
All examples demonstrate:

- Light and dark theme support
- Custom color schemes and accent colors
- Fluent Design styling principles
- Responsive design patterns
- Smooth animations and transitions

### 🔧 Interactive Features

- Real-time property adjustments with sliders and controls
- Live component configuration and preview
- Interactive demonstrations with immediate feedback
- Code examples and best practices embedded in UI
- Performance optimization techniques

### 📱 Responsive Design

- Adaptive layouts for different screen sizes
- Mobile-friendly touch interactions
- Accessibility features and keyboard navigation
- High DPI display support
- Cross-platform compatibility

## Running Examples

### Prerequisites

```bash
pip install pyside6>=6.5.0
# Or install the full project with dependencies
pip install -e .
```

### Individual Examples

Each example is self-contained and can be run independently:

```bash
# Layout examples
python examples/layout/layout_components_demo.py
python examples/layout/dock_panel_demo.py

# Basic component examples
python examples/basic/forms/forms_demo.py
python examples/basic/display/display_demo.py
python examples/basic/navigation/navigation_demo.py

# Data component examples
python examples/data/input/data_input_demo.py
python examples/data/display/data_display_demo.py
python examples/data/charts/data_charts_demo.py

# Other examples
python examples/composite/composite_demo.py
python examples/dialogs/dialog_components_demo.py
python examples/interface/interface_components_demo.py
python examples/media/media_controls_demo.py
python examples/controls/controls_demo.py
```

### Comprehensive Demo

For a complete overview of all components:

```bash
python examples/comprehensive_demo.py
```

## Code Structure

Each example follows a consistent structure:

```python
#!/usr/bin/env python3
"""
Component Demo Title

Description of what this demo showcases.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Standard imports
from PySide6.QtWidgets import QApplication, QMainWindow, ...

def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    
    # Component imports with fallbacks
    try:
        from components.category.component import FluentComponent
        COMPONENTS_AVAILABLE = True
    except ImportError:
        COMPONENTS_AVAILABLE = False
        # Fallback implementations using standard Qt widgets
    
    class ComponentDemo(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setup_ui()
        
        def setup_ui(self):
            # UI setup with examples and documentation
            pass
    
    demo = ComponentDemo()
    demo.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
```

## Best Practices Demonstrated

### 🏗️ Component Usage

- Proper initialization and configuration
- Event handling and signal connections
- State management patterns
- Performance optimization techniques
- Memory management and cleanup

### 🎨 Design Patterns

- Consistent visual hierarchy
- Fluent Design principles implementation
- Accessibility guidelines compliance
- Responsive layout strategies
- Progressive enhancement techniques

### 🔧 Development Practices

- Error handling and graceful fallbacks
- Component composition and reusability
- Testing and validation approaches
- Comprehensive documentation
- Cross-platform compatibility

## Troubleshooting

### Import Errors

If you encounter import errors:

1. Ensure you're running from the project root directory
2. Install all dependencies: `pip install -e .`
3. Verify Python path includes the project directory
4. Check that PySide6 is properly installed

### Component Not Available

Some examples include fallback implementations using standard Qt widgets when Fluent components are not yet implemented. This ensures all examples remain functional during development.

### Performance Issues

For better performance:

- Run examples individually rather than the comprehensive demo
- Disable animations if experiencing lag: set `ENABLE_ANIMATIONS = False`
- Use smaller datasets for data visualization examples
- Close other resource-intensive applications

### Display Issues

If you experience display problems:

- Ensure your graphics drivers are up to date
- Try running with software rendering: `QT_QUICK_BACKEND=software`
- Adjust DPI scaling if text appears too small/large
- Check system theme compatibility

## Contributing

When adding new examples:

1. **Follow the established directory structure**
   ```
   examples/
   ├── category/
   │   ├── subcategory/           # Optional
   │   │   └── example_demo.py
   │   └── category_demo.py
   ```

2. **Include comprehensive documentation**
   - Clear component descriptions
   - Usage examples and best practices
   - Code comments explaining key concepts
   - Interactive demonstrations

3. **Provide fallback implementations**
   - Handle missing components gracefully
   - Use standard Qt widgets as fallbacks
   - Display informative messages about component availability

4. **Add interactive controls**
   - Real-time property adjustments
   - Live configuration options
   - Multiple usage scenarios
   - Performance and accessibility considerations

5. **Update documentation**
   - Add example to this README
   - Include in the examples index
   - Document any special requirements
   - Add screenshots if helpful

## Development Status

### ✅ Completed Examples

- Layout Components (FluentStackPanel, Grid, ScrollViewer, Containers)
- Basic Components (Forms, Display, Navigation)
- Data Components (Input, Display, Charts)
- Composite Components (Complex layouts and forms)
- Dialog Components (Messages, Forms, Progress, Teaching Tips)
- Interface Components (Menus, Command Bars, Navigation)
- Media Components (Audio/Video, Image Viewers)
- Control Components (Pickers, Specialized Controls)

### 🚧 Future Enhancements

- Advanced animation examples
- Custom theme creation tutorials
- Performance optimization guides
- Accessibility feature demonstrations
- Mobile-specific interaction patterns

## License

All examples are provided under the MIT license, same as the main project.

---

For more information about the simple-fluent-widget library, see the main [README.md](../README.md) in the project root.
python examples/dialogs/dialog_components_demo.py
```

## Features Demonstrated

### Interactive Controls
- Real-time parameter adjustment with sliders and combo boxes
- Dynamic component creation and removal
- State management and event handling

### Theme Integration
- Light/dark theme switching
- Custom color schemes
- Responsive design patterns

### Best Practices
- Error handling and graceful fallbacks
- Accessibility considerations
- Performance optimization
- Component lifecycle management

### Responsive Design
- Window resizing behavior
- Content reflow and wrapping
- Adaptive layouts for different screen sizes

## Code Structure

Each example follows a consistent pattern:

```python
#!/usr/bin/env python3
"""
Component Demo - Description

This example demonstrates comprehensive usage of [Component] including
configuration, interaction, and best practices.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow
# ... other imports

def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    
    # Component imports with fallback handling
    try:
        from components.category.component import ComponentClass
        COMPONENTS_AVAILABLE = True
    except ImportError as e:
        print(f"Import error: {e}")
        COMPONENTS_AVAILABLE = False
    
    # Demo implementation with error handling
    # ...
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
```

## Error Handling

All examples include:
- Import error handling with informative messages
- Fallback to standard Qt widgets when Fluent components aren't available
- Graceful degradation of functionality
- User-friendly error messages

## Contributing

When adding new examples:

1. Follow the established directory structure
2. Include comprehensive documentation
3. Add interactive controls where appropriate
4. Implement proper error handling
5. Update this README with the new example

## Dependencies

- PySide6
- Python 3.8+
- simple-fluent-widget library components

## Troubleshooting

### Common Issues

**Import Errors**: If you see import errors, ensure the project root is in your Python path and all required dependencies are installed.

**Theme Issues**: Some stylesheet warnings are normal during development and don't affect functionality.

**Animation Warnings**: Property animation warnings are related to theme transitions and don't impact the core functionality.

### Getting Help

1. Check the individual example files for component-specific documentation
2. Review the main project README for setup instructions
3. Look at the `components/` directory for available components
4. Run `examples_index.py` for a guided tour of all examples

---

*Last updated: July 2025*
