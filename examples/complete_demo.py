"""
Complete Fluent UI Demo Application
Demonstrates usage and effects of all components
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTabWidget, QScrollArea, QGridLayout,
                               QGroupBox, QLabel, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import Fluent UI components
from components.basic.button import FluentButton, FluentIconButton, FluentToggleButton
from components.basic.textbox import FluentLineEdit, FluentTextEdit, FluentSearchBox
from components.basic.checkbox import FluentCheckBox, FluentRadioGroup, FluentSwitch
from core.theme import theme_manager, ThemeMode


class FluentDemoApp(QMainWindow):
    """Fluent UI Demo Application Main Window"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fluent UI for PySide6 - Complete Demo")
        self.setMinimumSize(1000, 700)

        # Setup central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)

        # Create toolbar
                # Create toolbar
        self._create_toolbar(main_layout)

        # Create tab interface
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self._create_button_demo()
        self._create_input_demo()
        self._create_selection_demo()
        self._create_layout_demo()

        # Apply theme
        self._apply_theme()

    def _create_toolbar(self, main_layout):
        """Create toolbar"""
        toolbar_layout = QHBoxLayout()

        # Theme toggle button
        self.theme_button = FluentToggleButton("🌙 Dark Theme")
        self.theme_button.toggled.connect(self._toggle_theme)
        toolbar_layout.addWidget(self.theme_button)

        # Add flexible space
        toolbar_layout.addItem(QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding))

        # About button
        about_button = FluentButton(
            "About", style=FluentButton.ButtonStyle.SECONDARY)
        about_button.clicked.connect(self._show_about)
        toolbar_layout.addWidget(about_button)

        main_layout.addLayout(toolbar_layout)
        
    def _create_button_demo(self):
        """Create button demo page"""
        scroll_area = QScrollArea()
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # Basic button group
        basic_group = QGroupBox("Basic Buttons")
        basic_layout = QGridLayout(basic_group)

        # Different style buttons
        primary_btn = FluentButton(
            "Primary Button", style=FluentButton.ButtonStyle.PRIMARY)
        secondary_btn = FluentButton(
            "Secondary Button", style=FluentButton.ButtonStyle.SECONDARY)
        accent_btn = FluentButton(
            "Accent Button", style=FluentButton.ButtonStyle.ACCENT)

        basic_layout.addWidget(primary_btn, 0, 0)
        basic_layout.addWidget(secondary_btn, 0, 1)
        basic_layout.addWidget(accent_btn, 0, 2)

        # 图标按钮
        icon_group = QGroupBox("图标按钮")
        icon_layout = QHBoxLayout(icon_group)

        # 注意：实际使用时需要提供真实的图标文件
        save_btn = FluentButton("💾 保存")
        delete_btn = FluentButton(
            "🗑️ 删除", style=FluentButton.ButtonStyle.SECONDARY)
        refresh_btn = FluentButton(
            "🔄 刷新", style=FluentButton.ButtonStyle.ACCENT)

        save_btn.clicked.connect(lambda: self._show_message("保存成功！"))
        delete_btn.clicked.connect(lambda: self._show_message("删除确认"))
        refresh_btn.clicked.connect(lambda: self._show_message("刷新中..."))

        icon_layout.addWidget(save_btn)
        icon_layout.addWidget(delete_btn)
        icon_layout.addWidget(refresh_btn)

        # 开关按钮组
        toggle_group = QGroupBox("开关按钮")
        toggle_layout = QVBoxLayout(toggle_group)

        toggle_btn1 = FluentToggleButton("功能开关 1")
        toggle_btn2 = FluentToggleButton("功能开关 2")

        toggle_btn1.toggled.connect(lambda checked:
                                    self._show_message(f"功能1 {'开启' if checked else '关闭'}"))
        toggle_btn2.toggled.connect(lambda checked:
                                    self._show_message(f"功能2 {'开启' if checked else '关闭'}"))

        toggle_layout.addWidget(toggle_btn1)
        toggle_layout.addWidget(toggle_btn2)

        layout.addWidget(basic_group)
        layout.addWidget(icon_group)
        layout.addWidget(toggle_group)
        layout.addStretch()

        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        self.tab_widget.addTab(scroll_area, "🔘 按钮组件")

    def _create_input_demo(self):
        """**创建输入组件演示页面**"""
        scroll_area = QScrollArea()
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # 文本输入组
        text_group = QGroupBox("文本输入")
        text_layout = QVBoxLayout(text_group)

        # 单行文本框
        line_edit = FluentLineEdit(placeholder="请输入您的姓名")
        text_layout.addWidget(QLabel("姓名:"))
        text_layout.addWidget(line_edit)

        # 密码框
        from components.basic.textbox import FluentPasswordEdit
        password_edit = FluentPasswordEdit()
        text_layout.addWidget(QLabel("密码:"))
        text_layout.addWidget(password_edit)

        # 多行文本框
        text_edit = FluentTextEdit()
        text_edit.setPlaceholderText("请输入详细描述...")
        text_edit.setMaximumHeight(100)
        text_layout.addWidget(QLabel("描述:"))
        text_layout.addWidget(text_edit)

        # 搜索框组
        search_group = QGroupBox("搜索框")
        search_layout = QVBoxLayout(search_group)

        search_box = FluentSearchBox()
        search_box.search_triggered.connect(lambda text:
                                            self._show_message(f"搜索: {text}"))

        search_layout.addWidget(search_box)

        layout.addWidget(text_group)
        layout.addWidget(search_group)
        layout.addStretch()

        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        self.tab_widget.addTab(scroll_area, "📝 输入组件")

    def _create_selection_demo(self):
        """**创建选择组件演示页面**"""
        scroll_area = QScrollArea()
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # 复选框组
        checkbox_group = QGroupBox("复选框")
        checkbox_layout = QVBoxLayout(checkbox_group)

        cb1 = FluentCheckBox("接收邮件通知")
        cb2 = FluentCheckBox("接收短信通知")
        cb3 = FluentCheckBox("记住登录状态")

        cb1.setChecked(True)

        cb1.stateChanged.connect(lambda state:
                                 self._show_message(f"邮件通知: {'开启' if state else '关闭'}"))

        checkbox_layout.addWidget(cb1)
        checkbox_layout.addWidget(cb2)
        checkbox_layout.addWidget(cb3)

        # 单选框组
        radio_group_widget = QGroupBox("单选框")
        radio_layout = QVBoxLayout(radio_group_widget)

        radio_group = FluentRadioGroup()
        radio_group.add_radio_button("小型")
        radio_group.add_radio_button("中型")
        radio_group.add_radio_button("大型")

        # 将单选按钮添加到布局
        for radio_button in radio_group.radio_buttons:
            radio_layout.addWidget(radio_button)

        radio_group.set_selected_index(1)
        radio_group.selection_changed.connect(lambda idx, text:
                                              self._show_message(f"选择: {text}"))

        # 开关组
        switch_group = QGroupBox("开关")
        switch_layout = QHBoxLayout(switch_group)

        switch1 = FluentSwitch()
        switch2 = FluentSwitch()

        switch1.set_checked(True)

        switch1.toggled.connect(lambda checked:
                                self._show_message(f"开关1: {'开' if checked else '关'}"))

        switch_layout.addWidget(QLabel("WiFi:"))
        switch_layout.addWidget(switch1)
        switch_layout.addWidget(QLabel("蓝牙:"))
        switch_layout.addWidget(switch2)
        switch_layout.addStretch()

        layout.addWidget(checkbox_group)
        layout.addWidget(radio_group_widget)
        layout.addWidget(switch_group)
        layout.addStretch()

        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        self.tab_widget.addTab(scroll_area, "☑️ 选择组件")

    def _create_layout_demo(self):
        """**创建布局演示页面**"""
        scroll_area = QScrollArea()
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # 卡片布局示例
        card_group = QGroupBox("卡片布局")
        card_layout = QGridLayout(card_group)

        for i in range(6):
            card = self._create_demo_card(f"卡片 {i+1}", f"这是第 {i+1} 个演示卡片")
            row, col = i // 3, i % 3
            card_layout.addWidget(card, row, col)

        # 信息展示区域
        info_group = QGroupBox("信息展示")
        info_layout = QVBoxLayout(info_group)

        self.info_label = QLabel("点击任意组件查看效果...")
        self.info_label.setWordWrap(True)
        self.info_label.setMinimumHeight(60)
        self.info_label.setStyleSheet(f"""
            QLabel {{
                background-color: {theme_manager.get_color('surface').name()};
                border: 1px solid {theme_manager.get_color('border').name()};
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                color: {theme_manager.get_color('text_secondary').name()};
            }}
        """)

        info_layout.addWidget(self.info_label)

        layout.addWidget(card_group)
        layout.addWidget(info_group)
        layout.addStretch()

        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        self.tab_widget.addTab(scroll_area, "🎨 布局展示")

    def _create_demo_card(self, title: str, description: str) -> QWidget:
        """创建演示卡片"""
        card = QWidget()
        card.setFixedHeight(120)

        # 应用卡片样式
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {theme_manager.get_color('card').name()};
                border: 1px solid {theme_manager.get_color('border').name()};
                border-radius: 8px;
                margin: 4px;
            }}
            QWidget:hover {{
                border-color: {theme_manager.get_color('primary').name()};
                background-color: {theme_manager.get_color('accent_light').name()};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {theme_manager.get_color('text_primary').name()};
                border: none;
                background: transparent;
            }}
        """)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {theme_manager.get_color('text_secondary').name()};
                border: none;
                background: transparent;
            }}
        """)

        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()

        return card

    def _toggle_theme(self, is_dark: bool):
        """**切换主题**"""
        if is_dark:
            theme_manager.set_theme_mode(ThemeMode.DARK)
            self.theme_button.setText("☀️ 亮色主题")
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)
            self.theme_button.setText("🌙 暗色主题")

        self._apply_theme()
        self._show_message(f"已切换到{'暗色' if is_dark else '亮色'}主题")

    def _apply_theme(self):
        """应用主题"""
        # 应用主窗口主题
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme_manager.get_color('background').name()};
                color: {theme_manager.get_color('text_primary').name()};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme_manager.get_color('border').name()};
                background-color: {theme_manager.get_color('surface').name()};
            }}
            QTabBar::tab {{
                background-color: {theme_manager.get_color('surface').name()};
                color: {theme_manager.get_color('text_primary').name()};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme_manager.get_color('primary').name()};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {theme_manager.get_color('accent_light').name()};
            }}
            QGroupBox {{
                font-weight: 600;
                font-size: 14px;
                color: {theme_manager.get_color('text_primary').name()};
                border: 1px solid {theme_manager.get_color('border').name()};
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }}
            QScrollArea {{
                border: none;
                background-color: {theme_manager.get_color('background').name()};
            }}
        """)

    def _show_message(self, message: str):
        """显示消息"""
        if hasattr(self, 'info_label'):
            self.info_label.setText(f"💡 {message}")
        print(f"FluentUI Demo: {message}")

    def _show_about(self):
        """显示关于信息"""
        self._show_message("Fluent UI for PySide6 - 现代化的UI组件库")


def main():
    """**主函数**"""
    app = QApplication(sys.argv)

    # 设置应用信息
    app.setApplicationName("Fluent UI Demo")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FluentUI")

    # 创建并显示主窗口
    window = FluentDemoApp()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
