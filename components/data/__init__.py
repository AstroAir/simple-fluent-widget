"""
Fluent Design Data Components

This module provides a comprehensive suite of data components organized by functionality:

- charts: Data visualization and charts
- input: Data input and form components  
- display: Data display and table components
- processing: Data processing utilities
- content: Specialized content viewers
- feedback: User feedback and status components
"""

# Import from organized submodules
from .charts import *
from .input import *
from .display import *
from .processing import *
from .content import *
from .feedback import *

# Legacy imports for backward compatibility (only import what exists)
from .content.rich_text import FluentRichTextEditor, FluentLinkDialog
from .input.colorpicker import FluentColorPicker, FluentColorWheel, FluentColorButton
from .charts.charts import FluentSimpleBarChart, FluentSimpleLineChart, FluentSimplePieChart, FluentGaugeChart
from .charts.advanced_charts import FluentAreaChart, FluentScatterChart, FluentHeatMap
from .display.property_grid import FluentPropertyGrid, FluentPropertyItem, PropertyType
from .content.json_viewer import OptimizedJsonTreeWidget

__all__ = [
    # Legacy exports for backward compatibility
    'FluentRichTextEditor', 'FluentLinkDialog',
    'FluentColorPicker', 'FluentColorWheel', 'FluentColorButton',
    'FluentSimpleBarChart', 'FluentSimpleLineChart', 'FluentSimplePieChart', 'FluentGaugeChart',
    'FluentAreaChart', 'FluentScatterChart', 'FluentHeatMap',
    'FluentPropertyGrid', 'FluentPropertyItem', 'PropertyType',
    'OptimizedJsonTreeWidget'
]