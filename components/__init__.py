"""
Fluent Design Components Package - Organized Structure

This package provides a comprehensive set of UI components organized by functionality:

- basic: Basic UI elements (forms, display, navigation, visual)
- data: Data-related components (charts, input, display, processing, content, feedback)
- interface: Interface control elements (command, navigation)
- layout: Layout and structural components (containers, dialogs)
- controls: Interactive controls (media, picker)
- composite: Complex composite components (forms, navigation, panels, toolbars)
"""

from . import basic
from . import data
from . import interface
from . import layout
from . import controls
from . import composite

__all__ = [
    'basic', 'data', 'interface', 'layout', 'controls', 'composite'
]