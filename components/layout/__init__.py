"""
Fluent UI Layout Components

This module contains comprehensive layout and container components that follow the Fluent Design System.
Includes cards, expanders, splitters, tabs, info bars, pivot controls, grids, scroll viewers, 
stack panels, flex layouts, dock panels, uniform grids, masonry layouts, adaptive layouts, and canvas.

Features modern layout patterns with consistent theming, responsive behavior, and smooth animations.
"""

# Import base classes
from .layout_base import FluentLayoutBase, FluentContainerBase, FluentAdaptiveLayoutBase

# Import layout components
from .flex_layout import (
    FluentFlexLayout, FlexDirection, FlexWrap, JustifyContent,
    AlignItems, AlignContent, FlexItem
)
from .dock_panel import FluentDockPanel, DockPosition, DockItem
from .additional_layouts import (
    FluentUniformGrid, FluentMasonryLayout, FluentAdaptiveLayout,
    FluentCanvas, MasonryItem, LayoutStrategy
)

# Import existing components (keeping for compatibility)
from .grid import FluentGrid, FluentGridItem, FluentGridBuilder, GridSpacing, GridItemAlignment
from .scroll_viewer import FluentScrollViewer, FluentScrollBar
from .stack_panel import FluentStackPanel, FluentWrapPanel, StackOrientation

# Import refactored containers
from .containers import (
    FluentCard,
    FluentExpander,
    FluentSplitter,
    FluentTabWidget,
    FluentInfoBar,
    FluentPivot
)

__all__ = [
    # Base classes
    'FluentLayoutBase',
    'FluentContainerBase',
    'FluentAdaptiveLayoutBase',

    # Modern layout components
    'FluentFlexLayout',
    'FlexDirection',
    'FlexWrap',
    'JustifyContent',
    'AlignItems',
    'AlignContent',
    'FlexItem',

    'FluentDockPanel',
    'DockPosition',
    'DockItem',

    'FluentUniformGrid',
    'FluentMasonryLayout',
    'FluentAdaptiveLayout',
    'FluentCanvas',
    'MasonryItem',
    'LayoutStrategy',

    # Container components
    'FluentCard',
    'FluentExpander',
    'FluentSplitter',
    'FluentTabWidget',
    'FluentInfoBar',
    'FluentPivot',

    # Existing components
    'FluentGrid',
    'FluentGridItem',
    'FluentGridBuilder',
    'GridSpacing',
    'GridItemAlignment',
    'FluentScrollViewer',
    'FluentScrollBar',
    'FluentStackPanel',
    'FluentWrapPanel',
    'StackOrientation'
]
