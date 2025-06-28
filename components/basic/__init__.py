"""
Basic Fluent Design Components - Organized Structure

This module provides basic UI components organized by functionality:

- forms: Interactive form controls and input elements
- display: Visual display and feedback elements  
- navigation: Navigation and structural elements
- visual: Visual and media elements
"""

# Import from organized submodules
from .forms import *
from .display import *
from .navigation import *
from .visual import *

# Legacy imports for backward compatibility
from .forms.button import FluentButton, FluentIconButton, FluentToggleButton
from .forms.textbox import FluentLineEdit, FluentTextEdit, FluentPasswordEdit, FluentSearchBox
from .forms.checkbox import FluentCheckBox, FluentRadioButton, FluentRadioGroup
from .display.tooltip import FluentTooltip, TooltipMixin
from .visual.rating import EnhancedFluentRating as FluentRating
from .navigation.tabs import FluentTabWidget, FluentTabButton
from .display.card import FluentCard
from .navigation.accordion import FluentAccordion, FluentAccordionItem
from .navigation.divider import FluentDivider, FluentSeparator, FluentSection
from .visual.avatar import FluentAvatar, FluentAvatarGroup
from .navigation.timeline import FluentTimeline, FluentTimelineItem
from .forms.switch import FluentSwitch as FluentModernSwitch, FluentSwitchGroup
from .display.loading import (FluentSpinner, FluentDotLoader, FluentProgressRing, 
                      FluentLoadingOverlay, FluentPulseLoader)
from .display.alert import EnhancedFluentAlert as FluentAlert, EnhancedFluentNotification as FluentNotification, FluentMessageBar, AlertType
from .display.badge import FluentBadge, FluentTag
from .navigation.pagination import FluentPagination, FluentSimplePagination
from .display.label import (FluentLabel, FluentIconLabel, FluentStatusLabel, 
                    FluentLinkLabel, FluentLabelGroup)
from .forms.switch import FluentSwitch

__all__ = [
    'FluentButton', 'FluentIconButton', 'FluentToggleButton',
    'FluentLineEdit', 'FluentTextEdit', 'FluentPasswordEdit', 'FluentSearchBox',
    'FluentCheckBox', 'FluentRadioButton', 'FluentRadioGroup', 'FluentSwitch',
    'FluentTooltip', 'TooltipMixin',
    'FluentRating',
    'FluentTabWidget', 'FluentTabButton',
    'FluentCard',
    'FluentAccordion', 'FluentAccordionItem',
    'FluentDivider', 'FluentSeparator', 'FluentSection',
    'FluentAvatar', 'FluentAvatarGroup',
    'FluentTimeline', 'FluentTimelineItem',
    'FluentModernSwitch', 'FluentSwitchGroup',
    'FluentSpinner', 'FluentDotLoader', 'FluentProgressRing', 'FluentLoadingOverlay', 'FluentPulseLoader',
    'FluentAlert', 'FluentNotification', 'FluentMessageBar', 'AlertType',
    'FluentBadge', 'FluentTag',
    'FluentPagination', 'FluentSimplePagination',
    'FluentLabel', 'FluentIconLabel', 'FluentStatusLabel', 'FluentLinkLabel', 'FluentLabelGroup'
]