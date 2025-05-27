# Simple Fluent Widget

A comprehensive Python library for creating modern, enterprise-grade user interfaces using Microsoft Fluent Design principles. Built with PyQt6, this library provides a rich set of components for data visualization, data entry, status displays, and more.

## 🚀 Features

- **7 Component Categories**: 30+ enterprise-focused UI components
- **Modern Design**: Follows Microsoft Fluent Design principles
- **High Performance**: Optimized for large datasets and real-time updates
- **Comprehensive Testing**: Full test coverage with performance benchmarks
- **Rich Documentation**: Auto-generated API docs and examples
- **Easy Integration**: Simple API with consistent patterns

## 📦 Installation

```bash
# Install from source
git clone https://github.com/yourusername/simple-fluent-widget.git
cd simple-fluent-widget
pip install -e .

# For development
pip install -e ".[dev]"

# For documentation generation
pip install -e ".[docs]"
```

## 🏗️ Component Categories

### 1. Data Visualization
- **Charts**: Line, bar, pie, scatter plots
- **Progress Components**: Progress rings, bars, indicators
- **Sparklines**: Compact trend visualization

### 2. Data Entry
- **Advanced Input**: Masked input, auto-complete
- **Rich Text Editor**: WYSIWYG text editing
- **Date/Time Pickers**: Calendar and time selection

### 3. Status & Notifications
- **Status Indicators**: Health, connection, process status
- **Progress Tracking**: Multi-step progress display
- **Badges & Pills**: Count indicators and tags

### 4. Tree & Hierarchical Data
- **Tree Widgets**: Expandable data structures
- **Organization Charts**: Hierarchical relationships
- **Breadcrumbs**: Navigation paths

### 5. Layout Containers
- **Cards**: Content grouping
- **Expanders**: Collapsible sections
- **Splitters**: Resizable panels
- **Info Bars**: Contextual messaging

### 6. Media Components
- **Image Viewer**: Advanced image display
- **Media Player**: Audio/video playback
- **Content Viewer**: Document and file preview

### 7. Command Interface
- **Command Bars**: Action organization
- **Toolbars**: Tool grouping
- **Ribbons**: Office-style interfaces

## 🎯 Quick Start

```python
import sys
from PyQt6.QtWidgets import QApplication
from simple_fluent_widget.components.basic import FluentButton
from simple_fluent_widget.components.data_viz import FluentChart

app = QApplication(sys.argv)

# Create a simple chart
chart = FluentChart()
chart.set_chart_type("line")
chart.set_data([1, 3, 2, 4, 3, 5])
chart.show()

app.exec()
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python build.py test

# Run performance benchmarks
python build.py benchmark

# Run integration tests only
python -m pytest tests/integration_test.py -v
```

## 📚 Documentation

Generate documentation:

```bash
# Generate all documentation
python build.py docs

# Generate specific docs
python tools/generate_docs.py
```

## 🎨 Demo Application

Explore all components with the comprehensive demo:

```bash
# Run demo application
python build.py demo

# Or directly
python examples/comprehensive_demo.py
```

## 🔧 Development

### Build Commands

```bash
# Install dependencies
python build.py install-deps

# Run linting
python build.py lint

# Build package
python build.py package

# Clean build artifacts
python build.py clean

# Full build pipeline
python build.py build
```

### Project Structure

```
simple-fluent-widget/
├── components/           # Core UI components
│   ├── basic/           # Basic widgets
│   ├── data_viz/        # Data visualization
│   ├── data_entry/      # Data input components
│   ├── status/          # Status indicators
│   ├── tree/            # Tree components
│   ├── layout/          # Layout containers
│   ├── media/           # Media components
│   └── command/         # Command interfaces
├── examples/            # Demo applications
├── tests/              # Test suite
├── tools/              # Build and dev tools
└── docs/               # Generated documentation
```

## 🎭 Theming

The library supports multiple themes:

```python
from simple_fluent_widget.theme import FluentTheme

# Apply theme
theme = FluentTheme()
theme.apply_theme(app, "dark")  # or "light"
```

## 📈 Performance

- **Memory Efficient**: Optimized for large datasets
- **Responsive UI**: Non-blocking operations
- **Scalable**: Handles thousands of data points
- **Benchmarked**: Comprehensive performance testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Microsoft Fluent Design System
- PyQt6 framework
- Python community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/simple-fluent-widget/issues)
- **Documentation**: [Auto-generated docs](./docs/)
- **Examples**: [Demo application](./examples/)

---

Made with ❤️ using Microsoft Fluent Design principles