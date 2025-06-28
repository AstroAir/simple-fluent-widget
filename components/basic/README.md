# Basic Components - Organized Structure

This document describes the reorganized folder structure for the basic components module.

## 📁 Folder Structure

The basic components have been reorganized into logical folders based on functionality:

### 📝 **forms/** - Form Controls and Input Elements
Interactive components for user input and form interactions:

- `button.py` - Button components (FluentButton, FluentIconButton, FluentToggleButton)
- `checkbox.py` - Checkbox and radio button components
- `combobox.py` - Dropdown selection components
- `slider.py` - Range slider components
- `spinbox.py` - Number input spinner components
- `switch.py` - Toggle switch components
- `textbox.py` - Text input components (FluentLineEdit, FluentTextEdit, etc.)
- `toggle.py` - Toggle button components

### 🖥️ **display/** - Visual Display and Feedback Elements
Components for displaying information and providing visual feedback:

- `alert.py` - Alert messages and notifications
- `badge.py` - Status badges and tags
- `card.py` - Content card containers
- `chip.py` - Tag chips and labels
- `label.py` - Text labels and status indicators
- `loading.py` - Loading spinners and progress indicators
- `progress.py` - Progress bars and indicators
- `tooltip.py` - Tooltip and hint components

### 🧭 **navigation/** - Navigation and Structural Elements
Components for navigation, layout, and content organization:

- `accordion.py` - Collapsible accordion sections
- `divider.py` - Visual separators and dividers
- `pagination.py` - Page navigation components
- `segmented.py` - Segmented control components
- `stepper.py` - Step-by-step navigation
- `tabs.py` - Tab navigation components
- `timeline.py` - Timeline display components

### 🎨 **visual/** - Visual and Media Elements
Visual components for user representation and media display:

- `avatar.py` - User avatar components
- `rating.py` - Rating star components

## 🔄 Backward Compatibility

The main `components.basic` module maintains full backward compatibility. All existing imports will continue to work:

```python
# These imports still work as before
from components.basic import FluentButton, FluentCard
from components.basic import FluentLineEdit, FluentTooltip
```

## 🚀 New Import Options

You can now also import from specific categories:

```python
# Import specific categories
from components.basic.forms import FluentButton, FluentLineEdit
from components.basic.display import FluentCard, FluentTooltip
from components.basic.navigation import FluentTabs, FluentAccordion
from components.basic.visual import FluentAvatar, FluentRating

# Import entire categories
from components.basic import forms, display, navigation, visual
```

## ✨ Benefits

1. **Logical Grouping** - Related components are organized by function
2. **Easier Discovery** - Find form controls, display elements, etc. quickly
3. **Better Maintenance** - Clearer organization for development
4. **Modular Imports** - Import only what you need from specific categories
5. **Scalable Structure** - Easy to add new components to appropriate categories
6. **Clear Intent** - Folder names clearly indicate component purposes

## 🔧 Component Categories Explained

### Forms Category
Interactive elements that users can manipulate to input data or trigger actions:
- Buttons, text inputs, checkboxes, sliders, switches
- Primary user interaction points

### Display Category  
Visual elements that present information or provide feedback:
- Cards, labels, badges, alerts, tooltips, loading indicators
- Information presentation and user feedback

### Navigation Category
Structural elements that help users navigate and organize content:
- Tabs, accordions, dividers, pagination, steppers
- Content organization and navigation

### Visual Category
Media and visual representation elements:
- Avatars, ratings, visual indicators
- User representation and visual content

## 📖 Usage Examples

### Form Controls
```python
from components.basic.forms import FluentButton, FluentLineEdit

button = FluentButton("Click me")
text_input = FluentLineEdit()
```

### Display Elements
```python
from components.basic.display import FluentCard, FluentAlert

card = FluentCard("Title", "Content")
alert = FluentAlert("Information", "This is important")
```

### Navigation Components
```python
from components.basic.navigation import FluentTabs, FluentAccordion

tabs = FluentTabs()
accordion = FluentAccordion()
```

### Visual Elements
```python
from components.basic.visual import FluentAvatar, FluentRating

avatar = FluentAvatar("User Name")
rating = FluentRating(5)
```

This organized structure maintains full functionality while providing better organization and improved developer experience.
