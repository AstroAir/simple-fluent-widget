"""
Label组件演示
展示各种Label组件的用法及与其他组件的组合使用
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QScrollArea, QGroupBox, QGridLayout, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap

from components.basic import (
    FluentLabel, FluentIconLabel, FluentStatusLabel, FluentLinkLabel, FluentLabelGroup,
    FluentButton, FluentCard, FluentCheckBox, FluentTextEdit
)
from core.theme import theme_manager


class LabelDemo(QMainWindow):
    """Label组件演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Label Components Demo")
        self.setGeometry(100, 100, 1000, 800)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 主内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加各种示例组
        content_layout.addWidget(self.create_basic_label_group())
        content_layout.addWidget(self.create_style_demo_group())
        content_layout.addWidget(self.create_type_demo_group())
        content_layout.addWidget(self.create_icon_label_group())
        content_layout.addWidget(self.create_status_label_group())
        content_layout.addWidget(self.create_link_label_group())
        content_layout.addWidget(self.create_combination_demo_group())
        content_layout.addWidget(self.create_label_group_demo())
        
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
    
    def create_basic_label_group(self) -> QGroupBox:
        """创建基础标签示例组"""
        group = QGroupBox("基础标签 (FluentLabel)")
        layout = QVBoxLayout(group)
        
        # 简单文本标签
        simple_label = FluentLabel("这是一个基础的Fluent标签")
        layout.addWidget(simple_label)
        
        # 可点击标签
        clickable_label = FluentLabel("这是一个可点击的标签")
        clickable_label.set_clickable(True)
        clickable_label.clicked.connect(lambda: print("标签被点击了!"))
        layout.addWidget(clickable_label)
        
        # 换行标签
        long_label = FluentLabel(
            "这是一个很长的标签文本，它会自动换行。这个标签展示了FluentLabel的自动换行功能，"
            "当文本超过容器宽度时会自动换到下一行显示。"
        )
        layout.addWidget(long_label)
        
        return group
    
    def create_style_demo_group(self) -> QGroupBox:
        """创建样式演示组"""
        group = QGroupBox("文字样式演示")
        layout = QVBoxLayout(group)
        
        styles = [
            (FluentLabel.LabelStyle.DISPLAY, "Display - 展示文字"),
            (FluentLabel.LabelStyle.TITLE_LARGE, "Title Large - 大标题"),
            (FluentLabel.LabelStyle.TITLE, "Title - 标题"),
            (FluentLabel.LabelStyle.SUBTITLE, "Subtitle - 副标题"),
            (FluentLabel.LabelStyle.BODY, "Body - 正文"),
            (FluentLabel.LabelStyle.CAPTION, "Caption - 说明文字"),
        ]
        
        for style, text in styles:
            label = FluentLabel(text, style=style)
            layout.addWidget(label)
        
        return group
    
    def create_type_demo_group(self) -> QGroupBox:
        """创建类型演示组"""
        group = QGroupBox("文字类型演示")
        layout = QVBoxLayout(group)
        
        types = [
            (FluentLabel.LabelType.PRIMARY, "Primary - 主要文字"),
            (FluentLabel.LabelType.SECONDARY, "Secondary - 次要文字"),
            (FluentLabel.LabelType.DISABLED, "Disabled - 禁用文字"),
            (FluentLabel.LabelType.ACCENT, "Accent - 强调文字"),
            (FluentLabel.LabelType.SUCCESS, "Success - 成功状态"),
            (FluentLabel.LabelType.WARNING, "Warning - 警告状态"),
            (FluentLabel.LabelType.ERROR, "Error - 错误状态"),
        ]
        
        for label_type, text in types:
            label = FluentLabel(text, label_type=label_type)
            layout.addWidget(label)
        
        return group
    
    def create_icon_label_group(self) -> QGroupBox:
        """创建图标标签示例组"""
        group = QGroupBox("图标标签 (FluentIconLabel)")
        layout = QVBoxLayout(group)
        
        # 注意：这里使用占位符图标，实际使用时应该使用真实的图标文件
        # 水平布局图标标签
        icon_label_h = FluentIconLabel("水平布局图标标签", layout_direction="horizontal")
        layout.addWidget(icon_label_h)
        
        # 垂直布局图标标签
        icon_label_v = FluentIconLabel("垂直布局图标标签", layout_direction="vertical")
        layout.addWidget(icon_label_v)
        
        # 可点击图标标签
        clickable_icon_label = FluentIconLabel("可点击的图标标签")
        clickable_icon_label.set_clickable(True)
        clickable_icon_label.clicked.connect(lambda: print("图标标签被点击了!"))
        layout.addWidget(clickable_icon_label)
        
        # 不同样式的图标标签
        title_icon_label = FluentIconLabel("标题样式图标标签")
        title_icon_label.set_text_style(FluentLabel.LabelStyle.TITLE)
        layout.addWidget(title_icon_label)
        
        return group
    
    def create_status_label_group(self) -> QGroupBox:
        """创建状态标签示例组"""
        group = QGroupBox("状态标签 (FluentStatusLabel)")
        layout = QVBoxLayout(group)
        
        statuses = [
            (FluentStatusLabel.StatusType.SUCCESS, "成功状态"),
            (FluentStatusLabel.StatusType.WARNING, "警告状态"),
            (FluentStatusLabel.StatusType.ERROR, "错误状态"),
            (FluentStatusLabel.StatusType.INFO, "信息状态"),
            (FluentStatusLabel.StatusType.PROCESSING, "处理中状态"),
        ]
        
        for status, text in statuses:
            status_label = FluentStatusLabel(text, status=status)
            layout.addWidget(status_label)
        
        # 无指示器的状态标签
        no_indicator_label = FluentStatusLabel("无指示器的状态标签", 
                                             status=FluentStatusLabel.StatusType.INFO,
                                             show_indicator=False)
        layout.addWidget(no_indicator_label)
        
        return group
    
    def create_link_label_group(self) -> QGroupBox:
        """创建链接标签示例组"""
        group = QGroupBox("链接标签 (FluentLinkLabel)")
        layout = QVBoxLayout(group)
        
        # 普通链接
        link_label = FluentLinkLabel("访问百度", "https://www.baidu.com")
        layout.addWidget(link_label)
        
        # 无URL链接（仅样式）
        style_link = FluentLinkLabel("样式链接（无跳转）")
        style_link.clicked.connect(lambda: print("样式链接被点击"))
        layout.addWidget(style_link)
        
        return group
    
    def create_combination_demo_group(self) -> QGroupBox:
        """创建组合使用演示组"""
        group = QGroupBox("与其他组件组合使用")
        layout = QVBoxLayout(group)
        
        # 1. 标签 + 按钮组合
        button_combo_layout = QHBoxLayout()
        combo_label = FluentLabel("选择操作:", style=FluentLabel.LabelStyle.SUBTITLE)
        combo_button = FluentButton("执行操作")
        combo_button.clicked.connect(lambda: combo_label.setText("操作已执行!"))
        
        button_combo_layout.addWidget(combo_label)
        button_combo_layout.addWidget(combo_button)
        button_combo_layout.addStretch()
        
        layout.addLayout(button_combo_layout)
        
        # 2. 标签 + 复选框组合
        checkbox_combo_layout = QHBoxLayout()
        checkbox_label = FluentLabel("启用功能:", style=FluentLabel.LabelStyle.BODY)
        checkbox = FluentCheckBox("启用")
        checkbox.stateChanged.connect(
            lambda state: checkbox_label.set_type(
                FluentLabel.LabelType.SUCCESS if state == 2 else FluentLabel.LabelType.PRIMARY
            )
        )
        
        checkbox_combo_layout.addWidget(checkbox_label)
        checkbox_combo_layout.addWidget(checkbox)
        checkbox_combo_layout.addStretch()
        
        layout.addLayout(checkbox_combo_layout)
        
        # 3. 卡片中的标签
        card = FluentCard()
        card_layout = QVBoxLayout(card)
        
        card_title = FluentLabel("卡片标题", style=FluentLabel.LabelStyle.TITLE)
        card_content = FluentLabel(
            "这是卡片中的内容标签。标签组件可以很好地与其他组件配合使用，"
            "提供一致的设计风格和用户体验。"
        )
        card_status = FluentStatusLabel("状态: 正常", status=FluentStatusLabel.StatusType.SUCCESS)
        
        card_layout.addWidget(card_title)
        card_layout.addWidget(card_content)
        card_layout.addWidget(card_status)
        
        layout.addWidget(card)
        
        return group
    
    def create_label_group_demo(self) -> QGroupBox:
        """创建标签组演示"""
        group = QGroupBox("标签组 (FluentLabelGroup)")
        layout = QVBoxLayout(group)
        
        # 水平标签组
        h_label_group = FluentLabelGroup(layout_direction="horizontal")
        h_label_group.add_label("标签1")
        h_label_group.add_label(FluentLabel("强调标签", label_type=FluentLabel.LabelType.ACCENT))
        h_label_group.add_label(FluentStatusLabel("状态标签", status=FluentStatusLabel.StatusType.SUCCESS))
        
        layout.addWidget(QFrame())  # 分隔线
        layout.addWidget(h_label_group)
        
        # 垂直标签组
        v_label_group = FluentLabelGroup(layout_direction="vertical", spacing=8)
        v_label_group.add_label(FluentLabel("垂直组标题", style=FluentLabel.LabelStyle.SUBTITLE))
        v_label_group.add_label("普通标签")
        v_label_group.add_label(FluentIconLabel("图标标签"))
        
        layout.addWidget(QFrame())  # 分隔线
        layout.addWidget(v_label_group)
        
        # 动态操作标签组
        dynamic_group = FluentLabelGroup()
        dynamic_group.add_label("初始标签")
        
        # 控制按钮
        button_layout = QHBoxLayout()
        add_button = FluentButton("添加标签")
        remove_button = FluentButton("移除最后一个标签")
        clear_button = FluentButton("清空标签")
        
        add_button.clicked.connect(
            lambda: dynamic_group.add_label(f"新标签 {len(dynamic_group.get_labels()) + 1}")
        )
        remove_button.clicked.connect(
            lambda: dynamic_group.remove_label(-1) if dynamic_group.get_labels() else None
        )
        clear_button.clicked.connect(dynamic_group.clear_labels)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        
        layout.addWidget(QFrame())  # 分隔线
        layout.addLayout(button_layout)
        layout.addWidget(dynamic_group)
        
        return group


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = LabelDemo()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
