"""
Fluent Design Pagination Component

Implements pagination controls with various modes and styles.
Based on Windows 11 Fluent Design principles.
"""

from typing import Optional
import math
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel,
                               QComboBox, QSpinBox)
from PySide6.QtCore import Qt, Signal

from core.theme import theme_manager
from core.enhanced_animations import FluentRevealEffect, FluentMicroInteraction, FluentTransition
from core.animation import FluentAnimation


class FluentPagination(QWidget):
    """
    Modern pagination component

    Features:
    - Multiple display modes (simple, full, compact)
    - Page size selection
    - Jump to specific page
    - Custom page range display
    - Responsive button states
    - Enhanced animations
    """

    # Signals
    page_changed = Signal(int)  # Page change signal
    page_size_changed = Signal(int)  # Page size change signal

    # Display modes
    MODE_SIMPLE = "simple"      # Simple mode: prev/next only
    MODE_FULL = "full"          # Full mode: includes page buttons
    MODE_COMPACT = "compact"    # Compact mode: core controls only

    def __init__(self,
                 total: int = 0,
                 page_size: int = 10,
                 current_page: int = 1,
                 mode: str = MODE_FULL,
                 show_page_size: bool = True,
                 show_jumper: bool = True,
                 show_total: bool = True,
                 page_size_options: Optional[list] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._total = total
        self._page_size = page_size
        self._current_page = current_page
        self._mode = mode
        self._show_page_size = show_page_size
        self._show_jumper = show_jumper
        self._show_total = show_total
        self._page_size_options = page_size_options or [10, 20, 50, 100]

        self._setup_ui()
        self._connect_theme()
        self._update_state()

    def _setup_ui(self):
        """Setup UI"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        # Total count display
        if self._show_total:
            self._total_label = QLabel()
            self._layout.addWidget(self._total_label)
            self._layout.addStretch()

        # Page size selection
        if self._show_page_size:
            self._page_size_label = QLabel("Items per page")
            self._page_size_combo = QComboBox()
            self._page_size_combo.setFixedWidth(80)

            for size in self._page_size_options:
                self._page_size_combo.addItem(str(size), size)

            self._page_size_combo.setCurrentText(str(self._page_size))
            self._page_size_combo.currentTextChanged.connect(
                self._on_page_size_changed)

            self._layout.addWidget(self._page_size_label)
            self._layout.addWidget(self._page_size_combo)

        # Pagination controls container
        self._pagination_container = QWidget()
        self._pagination_layout = QHBoxLayout(self._pagination_container)
        self._pagination_layout.setContentsMargins(0, 0, 0, 0)
        self._pagination_layout.setSpacing(4)

        # Previous page button
        self._prev_button = QPushButton("‹")
        self._prev_button.setFixedSize(32, 32)
        self._prev_button.clicked.connect(self._go_prev_page)
        self._prev_button.setToolTip("Previous page")

        # Add hover animation to prev button
        self._prev_button.enterEvent = lambda event: self._on_button_hover(
            self._prev_button)
        self._prev_button.leaveEvent = lambda event: self._on_button_leave(
            self._prev_button)

        self._pagination_layout.addWidget(self._prev_button)

        # Page buttons container
        self._page_buttons_container = QWidget()
        self._page_buttons_layout = QHBoxLayout(self._page_buttons_container)
        self._page_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._page_buttons_layout.setSpacing(2)
        self._pagination_layout.addWidget(self._page_buttons_container)

        # Next page button
        self._next_button = QPushButton("›")
        self._next_button.setFixedSize(32, 32)
        self._next_button.clicked.connect(self._go_next_page)
        self._next_button.setToolTip("Next page")

        # Add hover animation to next button
        self._next_button.enterEvent = lambda event: self._on_button_hover(
            self._next_button)
        self._next_button.leaveEvent = lambda event: self._on_button_leave(
            self._next_button)

        self._pagination_layout.addWidget(self._next_button)

        self._layout.addWidget(self._pagination_container)

        # Jump controls
        if self._show_jumper:
            self._jumper_label = QLabel("Go to page")
            self._jumper_spinbox = QSpinBox()
            self._jumper_spinbox.setFixedWidth(60)
            self._jumper_spinbox.setMinimum(1)
            self._jumper_spinbox.valueChanged.connect(self._on_jumper_changed)

            self._layout.addWidget(self._jumper_label)
            self._layout.addWidget(self._jumper_spinbox)

    def _on_button_hover(self, button: QPushButton):
        """Handle button hover with micro-interaction"""
        if button.isEnabled():
            FluentMicroInteraction.hover_glow(button, intensity=0.1)

    def _on_button_leave(self, button: QPushButton):
        """Handle button leave"""
        # Reset to normal state - could add fade out animation here
        pass

    def _on_button_click(self, button: QPushButton):
        """Handle button click with micro-interaction"""
        if button.isEnabled():
            FluentMicroInteraction.button_press(button, scale=0.95)

    def _connect_theme(self):
        """Connect to theme"""
        if theme_manager:
            theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """Update styles"""
        if not theme_manager:
            return
        theme = theme_manager

        # Base button styles
        button_style = f"""
            QPushButton {{
                background-color: {theme.get_color("background").name()};
                color: {theme.get_color("on_surface").name()};
                border: 1px solid {theme.get_color("border").name()};
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s ease;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color("primary").lighter(130).name()};
                border-color: {theme.get_color("primary").name()};
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color("primary").darker(110).name()};
                transform: translateY(0px);
            }}
            QPushButton:disabled {{
                background-color: {theme.get_color("surface_variant").name()};
                color: {theme.get_color("on_surface_variant").darker(120).name()};
                border-color: {theme.get_color("outline").name()};
            }}
        """

        # Apply styles to navigation buttons
        self._prev_button.setStyleSheet(button_style)
        self._next_button.setStyleSheet(button_style)

        # Label styles
        label_style = f"""
            QLabel {{
                color: {theme.get_color("on_surface").name()};
                font-size: 13px;
                font-weight: 400;
            }}
        """

        if hasattr(self, '_total_label'):
            self._total_label.setStyleSheet(label_style)
        if hasattr(self, '_page_size_label'):
            self._page_size_label.setStyleSheet(label_style)
        if hasattr(self, '_jumper_label'):
            self._jumper_label.setStyleSheet(label_style)

        # Input controls styles
        input_style = f"""
            QComboBox, QSpinBox {{
                background-color: {theme.get_color("background").name()};
                color: {theme.get_color("on_surface").name()};
                border: 1px solid {theme.get_color("border").name()};
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
                transition: border-color 0.2s ease;
            }}
            QComboBox:hover, QSpinBox:hover {{
                border-color: {theme.get_color("primary").name()};
            }}
            QComboBox:focus, QSpinBox:focus {{
                border-color: {theme.get_color("primary").name()};
                outline: none;
            }}
            QComboBox::drop-down {{
                border: none;
                border-radius: 0 6px 6px 0;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
        """

        if hasattr(self, '_page_size_combo'):
            self._page_size_combo.setStyleSheet(input_style)
        if hasattr(self, '_jumper_spinbox'):
            self._jumper_spinbox.setStyleSheet(input_style)

        self._update_page_buttons()

    def _update_page_buttons(self):
        """Update page buttons with enhanced animations"""
        # Clear existing buttons
        for i in reversed(range(self._page_buttons_layout.count())):
            item = self._page_buttons_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

        if self._mode == self.MODE_SIMPLE:
            return

        total_pages = self.get_total_pages()
        if total_pages <= 1 and self._mode != self.MODE_FULL:
            if self._mode == self.MODE_FULL and total_pages == 1:
                pass
            else:
                self._page_buttons_container.setVisible(False)
                return
        self._page_buttons_container.setVisible(True)

        page_range = self._calculate_page_range(total_pages)

        if not theme_manager:
            return
        theme = theme_manager

        # Create buttons with staggered reveal animation
        buttons_to_animate = []

        for index, page_num_or_ellipsis in enumerate(page_range):
            if page_num_or_ellipsis == "...":
                ellipsis_label = QLabel("...")
                ellipsis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                ellipsis_label.setFixedSize(32, 32)
                ellipsis_label.setStyleSheet(
                    f"color: {theme.get_color('on_surface').name()}; font-size: 14px;")
                self._page_buttons_layout.addWidget(ellipsis_label)
                buttons_to_animate.append(ellipsis_label)
            else:
                page_num = int(page_num_or_ellipsis)
                page_button = QPushButton(str(page_num))
                page_button.setFixedSize(32, 32)
                page_button.clicked.connect(
                    lambda _checked, p=page_num: self._on_page_button_clicked(p))
                page_button.setToolTip(f"Go to page {page_num}")

                # Add hover and click animations
                page_button.enterEvent = lambda event, btn=page_button: self._on_button_hover(
                    btn)
                page_button.leaveEvent = lambda event, btn=page_button: self._on_button_leave(
                    btn)

                if page_num == self._current_page:
                    page_button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {theme.get_color("primary").name()};
                            color: {theme.get_color("on_primary").name()};
                            border: 1px solid {theme.get_color("primary").name()};
                            border-radius: 6px;
                            font-size: 14px;
                            font-weight: 600;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }}
                        QPushButton:hover {{
                            background-color: {theme.get_color("primary").darker(110).name()};
                            transform: translateY(-1px);
                            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                        }}
                    """)
                else:
                    page_button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {theme.get_color("background").name()};
                            color: {theme.get_color("on_surface").name()};
                            border: 1px solid {theme.get_color("border").name()};
                            border-radius: 6px;
                            font-size: 14px;
                            font-weight: 500;
                            transition: all 0.2s ease;
                        }}
                        QPushButton:hover {{
                            background-color: {theme.get_color("primary").lighter(130).name()};
                            border-color: {theme.get_color("primary").name()};
                            transform: translateY(-1px);
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }}
                        QPushButton:pressed {{
                            background-color: {theme.get_color("primary").darker(110).name()};
                            transform: translateY(0px);
                        }}
                    """)

                self._page_buttons_layout.addWidget(page_button)
                buttons_to_animate.append(page_button)

        # Apply staggered reveal animation to new buttons
        if buttons_to_animate:
            FluentRevealEffect.staggered_reveal(
                buttons_to_animate, stagger_delay=50)

    def _on_page_button_clicked(self, page_num: int):
        """Handle page button click with animation"""
        # Find the clicked button and add press animation
        for i in range(self._page_buttons_layout.count()):
            item = self._page_buttons_layout.itemAt(i)
            if item:
                widget_candidate = item.widget()  # Get the widget once
                # Check if widget_candidate is an instance of QPushButton
                if isinstance(widget_candidate, QPushButton):
                    # Now, widget_candidate is known to be a QPushButton.
                    button = widget_candidate  # Assign to 'button'
                    if button.text() == str(page_num):
                        self._on_button_click(button)
                        break

        self.set_current_page(page_num)

    def _calculate_page_range(self, total_pages: int) -> list:
        """Calculate page range to display"""
        if total_pages <= 0:
            return []
        if total_pages <= 7:
            return list(range(1, total_pages + 1))

        current = self._current_page
        page_range = []

        # Always show first page
        page_range.append(1)

        # Ellipsis after first page
        if current > 4:
            page_range.append("...")

        # Middle pages
        start_middle = max(2, current - 1)
        end_middle = min(total_pages - 1, current + 1)

        if current <= 4:
            start_middle = 2
            end_middle = min(total_pages - 1, 5)
        elif current >= total_pages - 3:
            start_middle = max(2, total_pages - 4)
            end_middle = total_pages - 1

        for i in range(start_middle, end_middle + 1):
            if i not in page_range:
                page_range.append(i)

        # Ellipsis before last page
        if current < total_pages - 3 and end_middle < total_pages - 1:
            if "..." not in page_range[len(page_range)-2:]:
                page_range.append("...")

        # Always show last page if more than 1 page
        if total_pages > 1 and total_pages not in page_range:
            page_range.append(total_pages)

        # Clean up duplicates and unnecessary ellipsis
        final_range = []
        last_is_ellipsis = False
        for item in page_range:
            if item == "...":
                if not last_is_ellipsis:
                    final_range.append("...")
                last_is_ellipsis = True
            else:
                final_range.append(item)
                last_is_ellipsis = False

        # Remove unnecessary ellipsis
        i = 0
        while i < len(final_range) - 1:
            if final_range[i] == "..." and isinstance(final_range[i+1], int) and isinstance(final_range[i-1], int):
                if final_range[i+1] == final_range[i-1] + 1:
                    final_range.pop(i)
                    continue
            i += 1

        # Ensure proper structure
        if total_pages > 0 and (not final_range or final_range[0] != 1):
            if 1 in final_range:
                final_range.remove(1)
            final_range.insert(0, 1)

        if total_pages > 1:
            if final_range[-1] != total_pages:
                if total_pages in final_range:
                    final_range.remove(total_pages)
                if final_range[-1] == "...":
                    final_range.insert(len(final_range)-1, total_pages)
                else:
                    final_range.append(total_pages)

        # Final deduplication
        seen = set()
        deduped_final_range = []
        for item in final_range:
            if item == "...":
                if not deduped_final_range or deduped_final_range[-1] != "...":
                    deduped_final_range.append(item)
            elif item not in seen:
                seen.add(item)
                deduped_final_range.append(item)

        if total_pages <= 7:
            return list(range(1, total_pages + 1))

        return deduped_final_range

    def _update_state(self):
        """Update state with smooth transitions"""
        total_pages = self.get_total_pages()

        # Update button states with smooth transitions
        prev_enabled = self._current_page > 1
        next_enabled = self._current_page < total_pages or (
            total_pages == 0 and self._current_page == 1)

        # Animate button state changes
        if self._prev_button.isEnabled() != prev_enabled:
            self._prev_button.setEnabled(prev_enabled)
            if prev_enabled:
                FluentRevealEffect.fade_in(
                    self._prev_button, duration=FluentAnimation.DURATION_FAST)

        if self._next_button.isEnabled() != next_enabled:
            self._next_button.setEnabled(next_enabled)
            if next_enabled:
                FluentRevealEffect.fade_in(
                    self._next_button, duration=FluentAnimation.DURATION_FAST)

        # Update total display
        if hasattr(self, '_total_label'):
            if self._total == 0:
                new_text = "No items"
            else:
                start_item = (self._current_page - 1) * self._page_size + 1
                end_item = min(self._current_page *
                               self._page_size, self._total)
                new_text = f"Showing {start_item}-{end_item} of {self._total} items"

            if self._total_label.text() != new_text:
                self._total_label.setText(new_text)
                FluentRevealEffect.fade_in(
                    self._total_label, duration=FluentAnimation.DURATION_FAST)

        # Update jumper range
        if hasattr(self, '_jumper_spinbox'):
            self._jumper_spinbox.setMaximum(max(1, total_pages))
            if self._total == 0:
                self._jumper_spinbox.setValue(1)
                self._jumper_spinbox.setEnabled(False)
            else:
                self._jumper_spinbox.setValue(self._current_page)
                self._jumper_spinbox.setEnabled(True)

        # Update page buttons
        self._update_page_buttons()
        self._update_visibility()

    def _update_visibility(self):
        """Update control visibility with animations"""
        is_simple_mode = self._mode == self.MODE_SIMPLE
        has_items = self._total > 0
        total_pages = self.get_total_pages()

        # Animate visibility changes
        if hasattr(self, '_total_label'):
            should_show = self._show_total and not is_simple_mode
            if self._total_label.isVisible() != should_show:
                if should_show:
                    self._total_label.setVisible(True)
                    FluentRevealEffect.slide_in(
                        self._total_label, direction="left")
                else:
                    self._total_label.setVisible(False)

        if hasattr(self, '_page_size_label'):
            should_show = self._show_page_size and not is_simple_mode and has_items
            if self._page_size_label.isVisible() != should_show:
                if should_show:
                    self._page_size_label.setVisible(True)
                    self._page_size_combo.setVisible(True)
                    FluentRevealEffect.slide_in(
                        self._page_size_label, direction="right")
                    FluentRevealEffect.slide_in(
                        self._page_size_combo, direction="right")
                else:
                    self._page_size_label.setVisible(False)
                    self._page_size_combo.setVisible(False)

        should_show_pagination = not is_simple_mode and (
            has_items or total_pages > 0)
        if self._pagination_container.isVisible() != should_show_pagination:
            if should_show_pagination:
                self._pagination_container.setVisible(True)
                FluentRevealEffect.scale_in(self._pagination_container)
            else:
                self._pagination_container.setVisible(False)

        if hasattr(self, '_jumper_label'):
            should_show = self._show_jumper and not is_simple_mode and has_items
            if self._jumper_label.isVisible() != should_show:
                if should_show:
                    self._jumper_label.setVisible(True)
                    self._jumper_spinbox.setVisible(True)
                    FluentRevealEffect.slide_in(
                        self._jumper_label, direction="right")
                    FluentRevealEffect.slide_in(
                        self._jumper_spinbox, direction="right")
                else:
                    self._jumper_label.setVisible(False)
                    self._jumper_spinbox.setVisible(False)

        # Page buttons container visibility
        if is_simple_mode or (total_pages == 0 and self._mode != self.MODE_FULL) or (total_pages == 1 and self._mode == self.MODE_COMPACT):
            self._page_buttons_container.setVisible(False)
        elif self._mode == self.MODE_FULL and total_pages == 0:
            self._page_buttons_container.setVisible(True)
        else:
            self._page_buttons_container.setVisible(True)

    def _on_page_size_changed(self, text: str):
        """Handle page size change"""
        try:
            new_size = int(text)
            if new_size <= 0:
                return

            if new_size != self._page_size:
                old_page_size = self._page_size
                self._page_size = new_size

                # Adjust current page to maintain data position
                first_item_on_current_page_old = (
                    self._current_page - 1) * old_page_size + 1
                new_current_page = math.ceil(
                    first_item_on_current_page_old / self._page_size)
                new_current_page = max(1, new_current_page)

                total_pages = self.get_total_pages()
                self._current_page = min(
                    new_current_page, total_pages) if total_pages > 0 else 1

                self._update_state()
                self.page_size_changed.emit(new_size)
                if self._current_page != new_current_page and not (self._current_page == 1 and new_current_page == 0):
                    self.page_changed.emit(self._current_page)

        except ValueError:
            if hasattr(self, '_page_size_combo'):
                self._page_size_combo.setCurrentText(str(self._page_size))

    def _on_jumper_changed(self, page: int):
        """Handle jumper page change"""
        if page != self._current_page and page >= 1:
            total_pages = self.get_total_pages()
            if page <= total_pages or (total_pages == 0 and page == 1):
                self.set_current_page(page)

    def _go_prev_page(self):
        """Go to previous page with animation"""
        if self._current_page > 1:
            self._on_button_click(self._prev_button)
            self.set_current_page(self._current_page - 1)

    def _go_next_page(self):
        """Go to next page with animation"""
        if self._current_page < self.get_total_pages():
            self._on_button_click(self._next_button)
            self.set_current_page(self._current_page + 1)

    def get_total_pages(self) -> int:
        """Get total pages"""
        if self._total == 0:
            return 0
        if self._page_size <= 0:
            return 1
        return max(1, math.ceil(self._total / self._page_size))

    def set_total(self, total: int):
        """Set total items"""
        self._total = max(0, total)

        total_pages = self.get_total_pages()
        if self._current_page > total_pages and total_pages > 0:
            self._current_page = total_pages
        elif total_pages == 0:
            self._current_page = 1

        self._update_state()

    def set_current_page(self, page: int):
        """Set current page with smooth transition"""
        total_pages = self.get_total_pages()

        if total_pages == 0:
            new_page = 1
        else:
            new_page = max(1, min(page, total_pages))

        if new_page != self._current_page:
            self._current_page = new_page
            self._update_state()
            self.page_changed.emit(new_page)
        else:
            self._update_state()

    def set_page_size(self, size: int):
        """Set page size"""
        if size <= 0:
            return

        if size != self._page_size:
            old_page_size = self._page_size
            self._page_size = size

            if hasattr(self, '_page_size_combo'):
                found = False
                for i in range(self._page_size_combo.count()):
                    if self._page_size_combo.itemData(i) == size:
                        self._page_size_combo.setCurrentIndex(i)
                        found = True
                        break
                if not found:
                    self._page_size_combo.setCurrentText(str(size))

            first_item_on_current_page_old = (
                self._current_page - 1) * old_page_size + 1
            new_current_page = math.ceil(
                first_item_on_current_page_old / self._page_size)
            new_current_page = max(1, new_current_page)

            total_pages = self.get_total_pages()
            self._current_page = min(
                new_current_page, total_pages) if total_pages > 0 else 1

            self._update_state()
            self.page_size_changed.emit(size)

    def get_current_page(self) -> int:
        """Get current page"""
        return self._current_page

    def get_page_size(self) -> int:
        """Get page size"""
        return self._page_size

    def get_total(self) -> int:
        """Get total items"""
        return self._total

    def set_mode(self, mode: str):
        """Set display mode"""
        if mode in [self.MODE_SIMPLE, self.MODE_FULL, self.MODE_COMPACT]:
            self._mode = mode
            self._update_state()


class FluentSimplePagination(QWidget):
    """
    Simplified pagination component with basic prev/next functionality
    """

    page_changed = Signal(int)

    def __init__(self,
                 current_page: int = 1,
                 has_prev: bool = False,
                 has_next: bool = True,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._current_page = current_page
        self._has_prev = has_prev
        self._has_next = has_next

        self._setup_ui()
        self._connect_theme()
        self._update_state()

    def _setup_ui(self):
        """Setup UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Previous button
        self._prev_button = QPushButton("Previous")
        self._prev_button.setFixedHeight(32)
        self._prev_button.clicked.connect(self._go_prev_page)
        self._prev_button.setToolTip("Go to previous page")

        # Add hover animations
        self._prev_button.enterEvent = lambda event: self._on_button_hover(
            self._prev_button)
        self._prev_button.leaveEvent = lambda event: self._on_button_leave(
            self._prev_button)

        layout.addWidget(self._prev_button)

        # Page info
        self._page_label = QLabel()
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._page_label)

        # Next button
        self._next_button = QPushButton("Next")
        self._next_button.setFixedHeight(32)
        self._next_button.clicked.connect(self._go_next_page)
        self._next_button.setToolTip("Go to next page")

        # Add hover animations
        self._next_button.enterEvent = lambda event: self._on_button_hover(
            self._next_button)
        self._next_button.leaveEvent = lambda event: self._on_button_leave(
            self._next_button)

        layout.addWidget(self._next_button)

    def _on_button_hover(self, button: QPushButton):
        """Handle button hover with micro-interaction"""
        if button.isEnabled():
            FluentMicroInteraction.hover_glow(button, intensity=0.1)

    def _on_button_leave(self, button: QPushButton):
        """Handle button leave"""
        pass

    def _connect_theme(self):
        """Connect to theme"""
        if theme_manager:
            theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """Update styles"""
        if not theme_manager:
            return
        theme = theme_manager

        button_style = f"""
            QPushButton {{
                background-color: {theme.get_color("background").name()};
                color: {theme.get_color("on_surface").name()};
                border: 1px solid {theme.get_color("border").name()};
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: 500;
                transition: all 0.2s ease;
            }}
            QPushButton:hover:enabled {{
                background-color: {theme.get_color("primary").lighter(130).name()};
                border-color: {theme.get_color("primary").name()};
                transform: translateY(-1px);
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            QPushButton:pressed:enabled {{
                background-color: {theme.get_color("primary").darker(110).name()};
                transform: translateY(0px);
            }}
            QPushButton:disabled {{
                background-color: {theme.get_color("surface_variant").name()};
                color: {theme.get_color("on_surface_variant").darker(120).name()};
                border-color: {theme.get_color("outline").name()};
            }}
        """

        self._prev_button.setStyleSheet(button_style)
        self._next_button.setStyleSheet(button_style)

        self._page_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.get_color("on_surface").name()};
                font-size: 13px;
                font-weight: 500;
                padding: 0 16px;
            }}
        """)

    def _update_state(self):
        """Update state with smooth transitions"""
        # Animate button state changes
        if self._prev_button.isEnabled() != self._has_prev:
            self._prev_button.setEnabled(self._has_prev)
            if self._has_prev:
                FluentRevealEffect.fade_in(
                    self._prev_button, duration=FluentAnimation.DURATION_FAST)

        if self._next_button.isEnabled() != self._has_next:
            self._next_button.setEnabled(self._has_next)
            if self._has_next:
                FluentRevealEffect.fade_in(
                    self._next_button, duration=FluentAnimation.DURATION_FAST)

        # Update page label with animation
        new_text = f"Page {self._current_page}"
        if self._page_label.text() != new_text:
            self._page_label.setText(new_text)
            FluentRevealEffect.fade_in(
                self._page_label, duration=FluentAnimation.DURATION_FAST)

    def _go_prev_page(self):
        """Go to previous page with animation"""
        if self._has_prev:
            FluentMicroInteraction.button_press(self._prev_button, scale=0.95)
            self._current_page -= 1
            self.page_changed.emit(self._current_page)

    def _go_next_page(self):
        """Go to next page with animation"""
        if self._has_next:
            FluentMicroInteraction.button_press(self._next_button, scale=0.95)
            self._current_page += 1
            self.page_changed.emit(self._current_page)

    def set_page_info(self, current_page: int, has_prev: bool, has_next: bool):
        """Set page information with smooth transitions"""
        self._current_page = current_page
        self._has_prev = has_prev
        self._has_next = has_next
        self._update_state()

    def get_current_page(self) -> int:
        """Get current page"""
        return self._current_page
