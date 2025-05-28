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


class FluentPagination(QWidget):
    """
    现代分页组件

    Features:
    - 多种显示模式（简单、完整、紧凑）
    - 每页大小选择
    - 跳转到指定页面
    - 自定义页面范围显示
    - 响应式按钮状态
    """

    # 信号
    page_changed = Signal(int)  # 页面变化
    page_size_changed = Signal(int)  # 每页大小变化

    # 显示模式
    MODE_SIMPLE = "simple"      # 简单模式：上一页/下一页
    MODE_FULL = "full"          # 完整模式：包含页码按钮
    MODE_COMPACT = "compact"    # 紧凑模式：只显示核心控件

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
        """设置UI"""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        # 总数显示
        if self._show_total:
            self._total_label = QLabel()
            self._layout.addWidget(self._total_label)
            self._layout.addStretch()

        # 每页大小选择
        if self._show_page_size:
            self._page_size_label = QLabel("每页")
            self._page_size_combo = QComboBox()
            self._page_size_combo.setFixedWidth(80)

            for size in self._page_size_options:
                self._page_size_combo.addItem(str(size), size)

            self._page_size_combo.setCurrentText(str(self._page_size))
            self._page_size_combo.currentTextChanged.connect(
                self._on_page_size_changed)

            self._page_size_unit_label = QLabel("条")

            self._layout.addWidget(self._page_size_label)
            self._layout.addWidget(self._page_size_combo)
            self._layout.addWidget(self._page_size_unit_label)

        # 分页控件容器
        self._pagination_container = QWidget()
        self._pagination_layout = QHBoxLayout(self._pagination_container)
        self._pagination_layout.setContentsMargins(0, 0, 0, 0)
        self._pagination_layout.setSpacing(4)

        # 上一页按钮
        self._prev_button = QPushButton("‹")
        self._prev_button.setFixedSize(32, 32)
        self._prev_button.clicked.connect(self._go_prev_page)
        self._pagination_layout.addWidget(self._prev_button)

        # 页码按钮容器
        self._page_buttons_container = QWidget()
        self._page_buttons_layout = QHBoxLayout(self._page_buttons_container)
        self._page_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self._page_buttons_layout.setSpacing(2)
        self._pagination_layout.addWidget(self._page_buttons_container)

        # 下一页按钮
        self._next_button = QPushButton("›")
        self._next_button.setFixedSize(32, 32)
        self._next_button.clicked.connect(self._go_next_page)
        self._pagination_layout.addWidget(self._next_button)

        self._layout.addWidget(self._pagination_container)

        # 跳转控件
        if self._show_jumper:
            self._jumper_label = QLabel("跳至")
            self._jumper_spinbox = QSpinBox()
            self._jumper_spinbox.setFixedWidth(60)
            self._jumper_spinbox.setMinimum(1)
            self._jumper_spinbox.valueChanged.connect(self._on_jumper_changed)
            self._jumper_unit_label = QLabel("页")

            self._layout.addWidget(self._jumper_label)
            self._layout.addWidget(self._jumper_spinbox)
            self._layout.addWidget(self._jumper_unit_label)

    def _connect_theme(self):
        """连接主题"""
        if theme_manager:
            theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """更新样式"""
        if not theme_manager:
            return
        theme = theme_manager

        # 按钮基础样式
        button_style = f"""
            QPushButton {{
                background-color: {theme.get_color("background").name()};
                color: {theme.get_color("on_surface").name()};
                border: 1px solid {theme.get_color("border").name()};
                border-radius: 4px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color("primary").lighter(130).name()};
                border-color: {theme.get_color("primary").name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color("primary").darker(110).name()};
            }}
            QPushButton:disabled {{
                background-color: {theme.get_color("surface_variant").name()};
                color: {theme.get_color("on_surface_variant").darker(120).name()};
                border-color: {theme.get_color("outline").name()};
            }}
        """

        # 应用样式到导航按钮
        self._prev_button.setStyleSheet(button_style)
        self._next_button.setStyleSheet(button_style)

        # 标签样式
        label_style = f"""
            QLabel {{
                color: {theme.get_color("on_surface").name()};
                font-size: 13px;
            }}
        """

        if hasattr(self, '_total_label'):
            self._total_label.setStyleSheet(label_style)
        if hasattr(self, '_page_size_label'):
            self._page_size_label.setStyleSheet(label_style)
            self._page_size_unit_label.setStyleSheet(label_style)
        if hasattr(self, '_jumper_label'):
            self._jumper_label.setStyleSheet(label_style)
            self._jumper_unit_label.setStyleSheet(label_style)

        # 下拉框和输入框样式
        input_style = f"""
            QComboBox, QSpinBox {{
                background-color: {theme.get_color("background").name()};
                color: {theme.get_color("on_surface").name()};
                border: 1px solid {theme.get_color("border").name()};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 13px;
            }}
            QComboBox:hover, QSpinBox:hover {{
                border-color: {theme.get_color("primary").name()};
            }}
            QComboBox::drop-down {{
                border: none;
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

        self._update_page_buttons()  # Styles for page buttons depend on theme

    def _update_page_buttons(self):
        """更新页码按钮"""
        # 清除现有按钮
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
        # Ensure at least one page button if mode is full and total_pages is 1
        if total_pages <= 1 and self._mode != self.MODE_FULL:
            if self._mode == self.MODE_FULL and total_pages == 1:
                pass  # allow to create page 1 button
            else:
                self._page_buttons_container.setVisible(False)
                return
        self._page_buttons_container.setVisible(True)

        page_range = self._calculate_page_range(total_pages)

        if not theme_manager:
            return
        theme = theme_manager

        for page_num_or_ellipsis in page_range:
            if page_num_or_ellipsis == "...":
                ellipsis_label = QLabel("...")
                ellipsis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                ellipsis_label.setFixedSize(32, 32)
                ellipsis_label.setStyleSheet(
                    f"color: {theme.get_color('on_surface').name()}; font-size: 14px;")
                self._page_buttons_layout.addWidget(ellipsis_label)
            else:
                page_num = int(page_num_or_ellipsis)
                page_button = QPushButton(str(page_num))
                page_button.setFixedSize(32, 32)
                page_button.clicked.connect(
                    lambda _checked, p=page_num: self.set_current_page(p))

                if page_num == self._current_page:
                    page_button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {theme.get_color("primary").name()};
                            color: {theme.get_color("on_primary").name()};
                            border: 1px solid {theme.get_color("primary").name()};
                            border-radius: 4px;
                            font-size: 14px;
                            font-weight: 600;
                        }}
                    """)
                else:
                    page_button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {theme.get_color("background").name()};
                            color: {theme.get_color("on_surface").name()};
                            border: 1px solid {theme.get_color("border").name()};
                            border-radius: 4px;
                            font-size: 14px;
                            font-weight: 500;
                        }}
                        QPushButton:hover {{
                            background-color: {theme.get_color("primary").lighter(130).name()};
                            border-color: {theme.get_color("primary").name()};
                        }}
                        QPushButton:pressed {{
                            background-color: {theme.get_color("primary").darker(110).name()};
                        }}
                    """)
                self._page_buttons_layout.addWidget(page_button)

    def _calculate_page_range(self, total_pages: int) -> list:
        """计算要显示的页码范围"""
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
            # Show 1, 2, 3, 4, 5, ..., total
            end_middle = min(total_pages - 1, 5)
        elif current >= total_pages - 3:
            # Show 1, ..., N-4, N-3, N-2, N-1, N
            start_middle = max(2, total_pages - 4)
            end_middle = total_pages - 1

        for i in range(start_middle, end_middle + 1):
            if i not in page_range:
                page_range.append(i)

        # Ellipsis before last page
        if current < total_pages - 3 and end_middle < total_pages - 1:
            # avoid double ellipsis
            if "..." not in page_range[len(page_range)-2:]:
                page_range.append("...")

        # Always show last page if more than 1 page
        if total_pages > 1 and total_pages not in page_range:
            page_range.append(total_pages)

        # Remove duplicate "..." if any, or leading/trailing "..." if not needed
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

        # Ensure ellipsis makes sense (e.g., not 1, ..., 2)
        i = 0
        while i < len(final_range) - 1:
            if final_range[i] == "..." and isinstance(final_range[i+1], int) and isinstance(final_range[i-1], int):
                if final_range[i+1] == final_range[i-1] + 1:
                    final_range.pop(i)
                    continue
            i += 1

        # Ensure first element is 1 if total_pages > 0
        if total_pages > 0 and (not final_range or final_range[0] != 1):
            if 1 in final_range:
                final_range.remove(1)  # remove if misplaced
            final_range.insert(0, 1)

        # Ensure last element is total_pages if total_pages > 1
        if total_pages > 1:
            if final_range[-1] != total_pages:
                if total_pages in final_range:
                    final_range.remove(total_pages)
                if final_range[-1] == "...":
                    final_range.insert(len(final_range)-1, total_pages)
                else:
                    final_range.append(total_pages)

        # Deduplicate final_range while preserving order
        seen = set()
        deduped_final_range = []
        for item in final_range:
            if item == "...":  # Allow multiple distinct ellipsis
                if not deduped_final_range or deduped_final_range[-1] != "...":
                    deduped_final_range.append(item)
            elif item not in seen:
                seen.add(item)
                deduped_final_range.append(item)

        # Final check for consecutive numbers around ellipsis
        i = 1
        while i < len(deduped_final_range) - 1:
            if deduped_final_range[i] == "..." and \
               isinstance(deduped_final_range[i-1], int) and \
               isinstance(deduped_final_range[i+1], int) and \
               deduped_final_range[i+1] == deduped_final_range[i-1] + 1:
                deduped_final_range.pop(i)  # Remove redundant ellipsis
            else:
                i += 1

        # Ensure no "..." if all pages can be shown
        if total_pages <= 7:
            return list(range(1, total_pages + 1))

        return deduped_final_range

    def _update_state(self):
        """更新状态"""
        total_pages = self.get_total_pages()

        # 更新按钮状态
        self._prev_button.setEnabled(self._current_page > 1)
        self._next_button.setEnabled(
            self._current_page < total_pages or total_pages == 0 and self._current_page == 1)

        # 更新总数显示
        if hasattr(self, '_total_label'):
            if self._total == 0:
                self._total_label.setText("共 0 条")
            else:
                start_item = (self._current_page - 1) * self._page_size + 1
                end_item = min(self._current_page *
                               self._page_size, self._total)
                self._total_label.setText(
                    f"共 {self._total} 条，第 {start_item}-{end_item} 条")

        # 更新跳转器范围
        if hasattr(self, '_jumper_spinbox'):
            self._jumper_spinbox.setMaximum(max(1, total_pages))
            if self._total == 0:  # If no items, jumper should be 1 and disabled or hidden
                self._jumper_spinbox.setValue(1)
                self._jumper_spinbox.setEnabled(False)
            else:
                self._jumper_spinbox.setValue(self._current_page)
                self._jumper_spinbox.setEnabled(True)

        # 更新页码按钮
        self._update_page_buttons()
        self._update_visibility()

    def _update_visibility(self):
        """更新控件的可见性"""
        is_simple_mode = self._mode == self.MODE_SIMPLE
        has_items = self._total > 0
        total_pages = self.get_total_pages()

        if hasattr(self, '_total_label'):
            self._total_label.setVisible(
                self._show_total and not is_simple_mode)
        if hasattr(self, '_page_size_label'):
            self._page_size_label.setVisible(
                self._show_page_size and not is_simple_mode and has_items)
            self._page_size_combo.setVisible(
                self._show_page_size and not is_simple_mode and has_items)
            self._page_size_unit_label.setVisible(
                self._show_page_size and not is_simple_mode and has_items)

        self._pagination_container.setVisible(not is_simple_mode and (
            has_items or total_pages > 0))  # Show if items or if explicitly set to show page 1 of 0

        if hasattr(self, '_jumper_label'):
            self._jumper_label.setVisible(
                self._show_jumper and not is_simple_mode and has_items)
            self._jumper_spinbox.setVisible(
                self._show_jumper and not is_simple_mode and has_items)
            self._jumper_unit_label.setVisible(
                self._show_jumper and not is_simple_mode and has_items)

        # Hide page buttons container if no pages to show or in simple mode
        if is_simple_mode or (total_pages == 0 and self._mode != self.MODE_FULL) or (total_pages == 1 and self._mode == self.MODE_COMPACT):
            self._page_buttons_container.setVisible(False)
        # Special case: show page 1 for 0 items in full mode
        elif self._mode == self.MODE_FULL and total_pages == 0:
            self._page_buttons_container.setVisible(True)
        else:
            self._page_buttons_container.setVisible(True)

    def _on_page_size_changed(self, text: str):
        """页面大小改变"""
        try:
            new_size = int(text)
            if new_size <= 0:
                return  # Page size must be positive

            if new_size != self._page_size:
                old_page_size = self._page_size
                self._page_size = new_size

                # 调整当前页面以保持数据位置的近似
                # Calculate the first item index on the current page with the old page size
                first_item_on_current_page_old = (
                    self._current_page - 1) * old_page_size + 1

                # Calculate the new current page based on the new page size
                # to keep the first_item_on_current_page_old visible
                new_current_page = math.ceil(
                    first_item_on_current_page_old / self._page_size)
                # Ensure page is at least 1
                new_current_page = max(1, new_current_page)

                total_pages = self.get_total_pages()
                self._current_page = min(
                    new_current_page, total_pages) if total_pages > 0 else 1

                self._update_state()
                self.page_size_changed.emit(new_size)
                # Emit page_changed only if the current page actually changed after adjustment
                # check also if new_current_page was 0
                if self._current_page != new_current_page and not (self._current_page == 1 and new_current_page == 0):
                    self.page_changed.emit(self._current_page)

        except ValueError:
            # Restore previous value if input is invalid
            if hasattr(self, '_page_size_combo'):
                self._page_size_combo.setCurrentText(str(self._page_size))

    def _on_jumper_changed(self, page: int):
        """跳转页面改变"""
        if page != self._current_page and page >= 1:
            total_pages = self.get_total_pages()
            if page <= total_pages or total_pages == 0 and page == 1:
                self.set_current_page(page)

    def _go_prev_page(self):
        """上一页"""
        if self._current_page > 1:
            self.set_current_page(self._current_page - 1)

    def _go_next_page(self):
        """下一页"""
        if self._current_page < self.get_total_pages():
            self.set_current_page(self._current_page + 1)

    def get_total_pages(self) -> int:
        """获取总页数"""
        if self._total == 0:
            return 0  # Or 1 if you want to show page 1 of 0
        if self._page_size <= 0:
            return 1  # Should not happen if validated
        return max(1, math.ceil(self._total / self._page_size))

    def set_total(self, total: int):
        """设置总条数"""
        self._total = max(0, total)

        total_pages = self.get_total_pages()
        if self._current_page > total_pages and total_pages > 0:
            self._current_page = total_pages
        elif total_pages == 0:  # if total items become 0
            self._current_page = 1  # Reset to page 1

        self._update_state()

    def set_current_page(self, page: int):
        """设置当前页面"""
        total_pages = self.get_total_pages()

        # If no items, current page should be 1
        if total_pages == 0:
            new_page = 1
        else:
            new_page = max(1, min(page, total_pages))

        if new_page != self._current_page:
            self._current_page = new_page
            self._update_state()
            self.page_changed.emit(new_page)
        # Even if page number is same, state might need update (e.g. jumper sync)
        else:
            self._update_state()

    def set_page_size(self, size: int):
        """设置每页大小"""
        if size <= 0:
            return  # Page size must be positive

        if size != self._page_size:
            old_page_size = self._page_size
            self._page_size = size

            if hasattr(self, '_page_size_combo'):
                # Check if the size is in options, if not, add it or handle
                found = False
                for i in range(self._page_size_combo.count()):
                    if self._page_size_combo.itemData(i) == size:
                        self._page_size_combo.setCurrentIndex(i)
                        found = True
                        break
                if not found:
                    # Optionally add the new size to combo if not present
                    # self._page_size_combo.addItem(str(size), size)
                    # self._page_size_combo.setCurrentText(str(size))
                    # Or just update text if it's meant to be an editable combo
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
            # Emit page_changed only if the current page actually changed after adjustment
            # if self._current_page != current_page_before_resize:
            #    self.page_changed.emit(self._current_page)

    def get_current_page(self) -> int:
        """获取当前页面"""
        return self._current_page

    def get_page_size(self) -> int:
        """获取每页大小"""
        return self._page_size

    def get_total(self) -> int:
        """获取总条数"""
        return self._total

    def set_mode(self, mode: str):
        """设置显示模式"""
        if mode in [self.MODE_SIMPLE, self.MODE_FULL, self.MODE_COMPACT]:
            self._mode = mode
            self._update_state()  # Full update to re-evaluate visibility and buttons


class FluentSimplePagination(QWidget):
    """
    简化版分页组件，只包含基本的上一页/下一页功能
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
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 上一页按钮
        self._prev_button = QPushButton("上一页")
        self._prev_button.setFixedHeight(32)
        self._prev_button.clicked.connect(self._go_prev_page)
        layout.addWidget(self._prev_button)

        # 页面信息
        self._page_label = QLabel()
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._page_label)

        # 下一页按钮
        self._next_button = QPushButton("下一页")
        self._next_button.setFixedHeight(32)
        self._next_button.clicked.connect(self._go_next_page)
        layout.addWidget(self._next_button)

    def _connect_theme(self):
        """连接主题"""
        if theme_manager:
            theme_manager.theme_changed.connect(self._update_style)
        self._update_style()

    def _update_style(self):
        """更新样式"""
        if not theme_manager:
            return
        theme = theme_manager

        button_style = f"""
            QPushButton {{
                background-color: {theme.get_color("background").name()};
                color: {theme.get_color("on_surface").name()};
                border: 1px solid {theme.get_color("border").name()};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover:enabled {{
                background-color: {theme.get_color("primary").lighter(130).name()};
                border-color: {theme.get_color("primary").name()};
            }}
            QPushButton:pressed:enabled {{
                background-color: {theme.get_color("primary").darker(110).name()};
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
                padding: 0 12px;
            }}
        """)

    def _update_state(self):
        """更新状态"""
        self._prev_button.setEnabled(self._has_prev)
        self._next_button.setEnabled(self._has_next)
        self._page_label.setText(f"第 {self._current_page} 页")

    def _go_prev_page(self):
        """上一页"""
        if self._has_prev:
            self._current_page -= 1
            self.page_changed.emit(self._current_page)
            # Assuming external logic will call set_page_info to update has_prev/has_next

    def _go_next_page(self):
        """下一页"""
        if self._has_next:
            self._current_page += 1
            self.page_changed.emit(self._current_page)
            # Assuming external logic will call set_page_info to update has_prev/has_next

    def set_page_info(self, current_page: int, has_prev: bool, has_next: bool):
        """设置页面信息"""
        self._current_page = current_page
        self._has_prev = has_prev
        self._has_next = has_next
        self._update_state()

    def get_current_page(self) -> int:
        """获取当前页面"""
        return self._current_page
