"""
Fluent UI Command Components - Optimized for Python 3.11+

This module contains command interface components that follow the Fluent Design System.
Includes command bars, toolbars, ribbons, menus, and command palettes with modern features.
"""

from .bars import (
    # Core components
    FluentCommandBar,
    FluentToolbar,
    FluentRibbon,
    FluentRibbonTab,
    FluentRibbonGroup,
    FluentQuickAccessToolbar,
    # Modern type definitions
    CommandPriority,
    CommandState,
    CommandInfo,
    CommandBarState,
    ToolbarActionInfo,
    ToolbarState,
    CommandBarProtocol
)
from .menus import (
    # Menu components
    FluentMenu,
    FluentContextMenu,
    FluentCommandPalette,
    FluentRibbon as FluentAdvancedRibbon,
    FluentRibbonTab as FluentAdvancedRibbonTab,
    # Modern type definitions
    MenuItemType,
    MenuItemState,
    FluentMenuItem,
    MenuState,
    MenuProtocol
)

__all__ = [
    # Core components
    'FluentCommandBar',
    'FluentToolbar',
    'FluentRibbon',
    'FluentRibbonTab',
    'FluentRibbonGroup',
    'FluentQuickAccessToolbar',
    'FluentMenu',
    'FluentContextMenu',
    'FluentCommandPalette',
    'FluentAdvancedRibbon',
    'FluentAdvancedRibbonTab',
    # Modern type definitions
    'CommandPriority',
    'CommandState',
    'CommandInfo',
    'CommandBarState',
    'ToolbarActionInfo',
    'ToolbarState',
    'CommandBarProtocol',
    'MenuItemType',
    'MenuItemState',
    'FluentMenuItem',
    'MenuState',
    'MenuProtocol'
]
