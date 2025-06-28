# Data Components - Organized Structure

This document describes the new organized folder structure for the data components module.

## 📁 Folder Structure

The data components have been reorganized into logical folders based on functionality:

### 🎯 **charts/** - Data Visualization
- `charts.py` - Basic chart components (bar, line, pie, gauge)
- `advanced_charts.py` - Advanced chart types (area, scatter, heatmap)
- `visualization.py` - Visualization utilities and helpers

### 📝 **input/** - Data Input Components
- `entry.py` - Data entry forms and input validation
- `colorpicker.py` - Color selection components
- `calendar.py` - Date/time picker components

### 📊 **display/** - Data Display Components
- `table.py` - Table and grid components
- `tree.py` - Tree view components
- `property_grid.py` - Property editor components
- `fileexplorer.py` - File system browser components

### ⚙️ **processing/** - Data Processing Utilities
- `filter_sort.py` - Data filtering and sorting utilities
- `formatters.py` - Data formatting and transformation utilities

### 📄 **content/** - Content Display Components
- `rich_text.py` - Rich text editor and viewer
- `json_viewer.py` - JSON data viewer with syntax highlighting

### 🔔 **feedback/** - User Feedback Components
- `notification.py` - Toast notifications and alerts
- `status.py` - Status indicators and badges

## 🔄 Backward Compatibility

The main `components.data` module maintains full backward compatibility. All existing imports will continue to work:

```python
# These imports still work as before
from components.data import FluentRichTextEditor, FluentColorPicker
from components.data import FluentSimpleBarChart, FluentPropertyGrid
```

## 🚀 New Import Options

You can now also import from specific categories:

```python
# Import specific categories
from components.data.charts import FluentSimpleBarChart, FluentAreaChart
from components.data.input import FluentColorPicker, FluentCalendar
from components.data.display import FluentTable, FluentTreeView
from components.data.processing import DataFilter, DataFormatter
from components.data.content import FluentRichTextEditor, JsonViewer
from components.data.feedback import FluentToast, StatusIndicator

# Import entire categories
from components.data import charts, input, display, processing, content, feedback
```

## ✨ Benefits

1. **Better Organization** - Related components are grouped together
2. **Clearer Intent** - Folder names clearly indicate component purposes
3. **Easier Navigation** - Developers can quickly find relevant components
4. **Modular Imports** - Import only what you need from specific categories
5. **Scalability** - Easy to add new components to appropriate categories
6. **Maintainability** - Logical grouping makes code maintenance easier

## 🔧 Python 3.11+ Optimizations

All components have been modernized with:
- ✅ Union type syntax (`|`) and PEP 604 compliance
- ✅ Dataclasses with slots and frozen optimizations
- ✅ Enhanced pattern matching and type safety
- ✅ Better error handling and validation
- ✅ Performance optimizations with caching
- ✅ Modern animation system integration
- ✅ Robust theme and style management

## 📖 Usage Examples

### Charts
```python
from components.data.charts import FluentSimpleBarChart
chart = FluentSimpleBarChart(data=[1, 2, 3, 4])
```

### Input Components
```python
from components.data.input import FluentColorPicker
picker = FluentColorPicker()
```

### Display Components
```python
from components.data.display import FluentTable
table = FluentTable()
```

### Processing Utilities
```python
from components.data.processing import DataFilter
filtered_data = DataFilter.apply_filters(data, filters)
```

This organized structure maintains full functionality while providing better organization and developer experience.
