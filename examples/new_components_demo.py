#!/usr/bin/env python3
"""
New Components Demo Application

This demo showcases the newly added Fluent UI components including:
- Accordion (collapsible panels)
- Divider (visual separators)
- Avatar (user avatars)
- Timeline (chronological events)
- Breadcrumb (navigation)
- Color Picker (color selection)
"""

import sys
import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QScrollArea, QTabWidget, QWidget, QGroupBox,
    QLabel, QPushButton, QTextEdit, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPixmap

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import new components
from components.basic.accordion import FluentAccordion
from components.basic.divider import FluentDivider, FluentSection
from components.basic.avatar import FluentAvatar, FluentAvatarGroup
from components.basic.timeline import FluentTimeline, FluentTimelineItem
from components.navigation.breadcrumb import FluentBreadcrumb
from components.data.colorpicker import FluentColorPicker

# Import existing components for comparison
from components.basic.card import FluentCard
from components.basic.button import FluentButton
from core.theme import theme_manager


class ComponentDemoTab(QWidget):
    """Base class for component demonstration tabs"""
    
    def __init__(self, title: str, description: str):
        super().__init__()
        self.title = title
        self.description = description
        self.setup_ui()
        self.setup_content()
    
    def setup_ui(self):
        """Setup basic UI structure"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_font = QFont()
        desc_font.setPointSize(12)
        desc_label.setFont(desc_font)
        layout.addWidget(desc_label)
        
        # Content area
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
        
        # Stretch
        layout.addStretch()
    
    def setup_content(self):
        """Override in subclasses"""
        pass


class AccordionDemo(ComponentDemoTab):
    """Demo for accordion component"""
    
    def __init__(self):
        super().__init__(
            "手风琴组件 (Accordion)",
            "可折叠的内容面板，支持单选或多选展开模式，带有平滑动画效果"
        )
    
    def setup_content(self):
        # Single selection accordion
        single_group = QGroupBox("单选模式")
        single_layout = QVBoxLayout(single_group)
        
        self.single_accordion = FluentAccordion()
        self.single_accordion.setAllowMultipleExpanded(False)
        
        # Add items
        settings_content = QWidget()
        settings_layout = QVBoxLayout(settings_content)
        settings_layout.addWidget(QLabel("主题设置"))
        settings_layout.addWidget(QPushButton("切换主题"))
        settings_layout.addWidget(QLabel("语言设置"))
        settings_layout.addWidget(QPushButton("选择语言"))
        
        self.single_accordion.addItem("系统设置", settings_content)
        
        profile_content = QWidget()
        profile_layout = QVBoxLayout(profile_content)
        profile_layout.addWidget(QLabel("个人信息"))
        profile_layout.addWidget(QPushButton("编辑资料"))
        profile_layout.addWidget(QLabel("头像设置"))
        profile_layout.addWidget(QPushButton("上传头像"))
        
        self.single_accordion.addItem("用户资料", profile_content)
        
        security_content = QWidget()
        security_layout = QVBoxLayout(security_content)
        security_layout.addWidget(QLabel("密码管理"))
        security_layout.addWidget(QPushButton("修改密码"))
        security_layout.addWidget(QLabel("两步验证"))
        security_layout.addWidget(QPushButton("启用2FA"))
        
        self.single_accordion.addItem("安全设置", security_content)
        
        single_layout.addWidget(self.single_accordion)
        
        # Multiple selection accordion
        multi_group = QGroupBox("多选模式")
        multi_layout = QVBoxLayout(multi_group)
        
        self.multi_accordion = FluentAccordion()
        self.multi_accordion.setAllowMultipleExpanded(True)
        
        # FAQ items
        faq1_content = QLabel("您可以在设置页面中切换明暗主题，或者使用快捷键 Ctrl+T")
        faq1_content.setWordWrap(True)
        self.multi_accordion.addItem("如何切换主题？", faq1_content)
        
        faq2_content = QLabel("目前支持中文、英文、日文等多种语言，可在语言设置中选择")
        faq2_content.setWordWrap(True)
        self.multi_accordion.addItem("支持哪些语言？", faq2_content)
        
        faq3_content = QLabel("您可以通过邮件、在线客服或者官方论坛联系我们的技术支持团队")
        faq3_content.setWordWrap(True)
        self.multi_accordion.addItem("如何联系技术支持？", faq3_content)
        
        multi_layout.addWidget(self.multi_accordion)
        
        # Layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(single_group)
        main_layout.addWidget(multi_group)
        
        self.content_layout.addLayout(main_layout)


class DividerDemo(ComponentDemoTab):
    """Demo for divider component"""
    
    def __init__(self):
        super().__init__(
            "分隔线组件 (Divider)",
            "各种样式的视觉分隔线，支持水平、垂直方向，以及不同的线条样式"
        )
    
    def setup_content(self):
        # Basic dividers
        basic_group = QGroupBox("基本分隔线")
        basic_layout = QVBoxLayout(basic_group)
        
        basic_layout.addWidget(QLabel("内容区域 1"))
        
        solid_divider = FluentDivider()
        basic_layout.addWidget(solid_divider)
        
        basic_layout.addWidget(QLabel("内容区域 2"))
        
        dashed_divider = FluentDivider()
        dashed_divider.setStyle(FluentDivider.Style.DASHED)
        basic_layout.addWidget(dashed_divider)
        
        basic_layout.addWidget(QLabel("内容区域 3"))
        
        # Text dividers
        text_group = QGroupBox("带文字的分隔线")
        text_layout = QVBoxLayout(text_group)
        
        text_layout.addWidget(QLabel("第一部分内容"))
        
        text_divider1 = FluentDivider()
        text_divider1.setText("重要提示")
        text_divider1.setTextPosition(0.5)  # Center
        text_layout.addWidget(text_divider1)
        
        text_layout.addWidget(QLabel("第二部分内容"))
        
        text_divider2 = FluentDivider()
        text_divider2.setText("更多信息")
        text_divider2.setTextPosition(0.2)  # Left-aligned
        text_divider2.setStyle(FluentDivider.Style.GRADIENT)
        text_layout.addWidget(text_divider2)
        
        text_layout.addWidget(QLabel("第三部分内容"))
        
        # Section divider
        section_group = QGroupBox("章节分隔")
        section_layout = QVBoxLayout(section_group)
        
        section1 = FluentSection("用户管理", "管理系统中的所有用户账户")
        section_layout.addWidget(section1)
        section_layout.addWidget(QLabel("用户列表、权限设置、角色管理等功能"))
        
        section2 = FluentSection("系统配置", "系统级别的配置选项")
        section_layout.addWidget(section2)
        section_layout.addWidget(QLabel("数据库设置、缓存配置、日志级别等"))
        
        # Vertical dividers
        vertical_group = QGroupBox("垂直分隔线")
        vertical_content = QWidget()
        vertical_layout = QHBoxLayout(vertical_content)
        
        vertical_layout.addWidget(QLabel("左侧内容"))
        
        v_divider1 = FluentDivider(FluentDivider.Orientation.VERTICAL)
        vertical_layout.addWidget(v_divider1)
        
        vertical_layout.addWidget(QLabel("中间内容"))
        
        v_divider2 = FluentDivider(FluentDivider.Orientation.VERTICAL)
        v_divider2.setStyle(FluentDivider.Style.DASHED)
        vertical_layout.addWidget(v_divider2)
        
        vertical_layout.addWidget(QLabel("右侧内容"))
        
        vertical_group_layout = QVBoxLayout(vertical_group)
        vertical_group_layout.addWidget(vertical_content)
        
        # Main layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(basic_group)
        top_layout.addWidget(text_group)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(section_group)
        bottom_layout.addWidget(vertical_group)
        
        self.content_layout.addLayout(top_layout)
        self.content_layout.addLayout(bottom_layout)


class AvatarDemo(ComponentDemoTab):
    """Demo for avatar component"""
    
    def __init__(self):
        super().__init__(
            "头像组件 (Avatar)", 
            "用户头像显示，支持照片、首字母、图标等多种模式，以及不同尺寸和形状"
        )
    
    def setup_content(self):
        # Size demo
        size_group = QGroupBox("不同尺寸")
        size_layout = QHBoxLayout(size_group)
        
        sizes = [
            (FluentAvatar.Size.SMALL, "小"),
            (FluentAvatar.Size.MEDIUM, "中"),
            (FluentAvatar.Size.LARGE, "大"),
            (FluentAvatar.Size.XLARGE, "特大"),
            (FluentAvatar.Size.XXLARGE, "超大")
        ]
        
        for size, label in sizes:
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            avatar = FluentAvatar(size)
            avatar.setName("用户")
            container_layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignCenter)
            container_layout.addWidget(QLabel(label), 0, Qt.AlignmentFlag.AlignCenter)
            
            size_layout.addWidget(container)
        
        # Shape demo
        shape_group = QGroupBox("不同形状")
        shape_layout = QHBoxLayout(shape_group)
        
        shapes = [
            (FluentAvatar.Shape.CIRCLE, "圆形"),
            (FluentAvatar.Shape.ROUNDED_SQUARE, "圆角方形"),
            (FluentAvatar.Shape.SQUARE, "方形")
        ]
        
        for shape, label in shapes:
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            avatar = FluentAvatar(FluentAvatar.Size.LARGE, shape)
            avatar.setName("测试用户")
            container_layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignCenter)
            container_layout.addWidget(QLabel(label), 0, Qt.AlignmentFlag.AlignCenter)
            
            shape_layout.addWidget(container)
        
        # Style demo
        style_group = QGroupBox("不同样式")
        style_layout = QHBoxLayout(style_group)
        
        # Initials avatar
        initials_container = QWidget()
        initials_layout = QVBoxLayout(initials_container)
        initials_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        initials_avatar = FluentAvatar(FluentAvatar.Size.LARGE)
        initials_avatar.setName("张三")
        initials_layout.addWidget(initials_avatar, 0, Qt.AlignmentFlag.AlignCenter)
        initials_layout.addWidget(QLabel("首字母"), 0, Qt.AlignmentFlag.AlignCenter)
        
        # Icon avatar
        icon_container = QWidget()
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_avatar = FluentAvatar(FluentAvatar.Size.LARGE)
        icon_avatar.setIcon("person")
        icon_layout.addWidget(icon_avatar, 0, Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(QLabel("图标"), 0, Qt.AlignmentFlag.AlignCenter)
        
        # Clickable avatar
        clickable_container = QWidget()
        clickable_layout = QVBoxLayout(clickable_container)
        clickable_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        clickable_avatar = FluentAvatar(FluentAvatar.Size.LARGE)
        clickable_avatar.setName("李四")
        clickable_avatar.setClickable(True)
        clickable_avatar.setBorderWidth(2)
        clickable_avatar.clicked.connect(lambda: print("头像被点击"))
        clickable_layout.addWidget(clickable_avatar, 0, Qt.AlignmentFlag.AlignCenter)
        clickable_layout.addWidget(QLabel("可点击"), 0, Qt.AlignmentFlag.AlignCenter)
        
        style_layout.addWidget(initials_container)
        style_layout.addWidget(icon_container)
        style_layout.addWidget(clickable_container)
        
        # Avatar group demo
        group_demo = QGroupBox("头像组")
        group_layout = QVBoxLayout(group_demo)
        
        avatar_group = FluentAvatarGroup(max_visible=4)
        
        # Add avatars to group
        names = ["王五", "赵六", "孙七", "周八", "吴九", "郑十"]
        for name in names:
            avatar = FluentAvatar(FluentAvatar.Size.MEDIUM)
            avatar.setName(name)
            avatar_group.addAvatar(avatar)
        
        group_layout.addWidget(QLabel("团队成员:"))
        group_layout.addWidget(avatar_group)
        
        # Main layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(size_group)
        top_layout.addWidget(shape_group)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(style_group)
        bottom_layout.addWidget(group_demo)
        
        self.content_layout.addLayout(top_layout)
        self.content_layout.addLayout(bottom_layout)


class TimelineDemo(ComponentDemoTab):
    """Demo for timeline component"""
    
    def __init__(self):
        super().__init__(
            "时间线组件 (Timeline)",
            "显示按时间顺序排列的事件，支持不同状态和自定义内容"
        )
    
    def setup_content(self):
        # Basic timeline
        basic_group = QGroupBox("基本时间线")
        basic_layout = QVBoxLayout(basic_group)
        
        self.basic_timeline = FluentTimeline()
        self.basic_timeline.setMaximumHeight(300)
        
        # Add events
        now = datetime.now()
        events = [
            ("项目启动", "正式启动新产品开发项目", now - timedelta(days=30), FluentTimelineItem.Status.COMPLETED),
            ("需求分析", "完成用户需求分析和产品规划", now - timedelta(days=25), FluentTimelineItem.Status.COMPLETED),
            ("UI设计", "界面设计和用户体验优化", now - timedelta(days=20), FluentTimelineItem.Status.COMPLETED),
            ("开发阶段", "前端和后端代码开发", now - timedelta(days=10), FluentTimelineItem.Status.CURRENT),
            ("测试阶段", "功能测试和性能优化", now + timedelta(days=5), FluentTimelineItem.Status.PENDING),
            ("产品发布", "正式发布产品上线", now + timedelta(days=15), FluentTimelineItem.Status.PENDING),
        ]
        
        for title, desc, timestamp, status in events:
            self.basic_timeline.addItem(title, desc, timestamp, status)
        
        basic_layout.addWidget(self.basic_timeline)
        
        # Interactive timeline
        interactive_group = QGroupBox("交互式时间线")
        interactive_layout = QVBoxLayout(interactive_group)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        add_btn = FluentButton("添加事件")
        add_btn.clicked.connect(self.add_timeline_event)
        
        clear_btn = FluentButton("清空")
        clear_btn.clicked.connect(self.clear_timeline)
        
        reverse_btn = FluentButton("倒序")
        reverse_btn.clicked.connect(self.toggle_timeline_order)
        
        controls_layout.addWidget(add_btn)
        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(reverse_btn)
        controls_layout.addStretch()
        
        interactive_layout.addLayout(controls_layout)
        
        # Interactive timeline
        self.interactive_timeline = FluentTimeline()
        self.interactive_timeline.setMaximumHeight(250)
        self.interactive_timeline.item_clicked.connect(self.on_timeline_item_clicked)
        
        # Add some initial events
        self.interactive_timeline.addItem(
            "系统初始化", 
            "应用程序启动完成",
            now - timedelta(minutes=5),
            FluentTimelineItem.Status.COMPLETED
        )
        
        interactive_layout.addWidget(self.interactive_timeline)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(basic_group)
        main_layout.addWidget(interactive_group)
        
        self.content_layout.addLayout(main_layout)
    
    def add_timeline_event(self):
        """Add new timeline event"""
        import random
        
        events = [
            ("新用户注册", "用户张三完成注册"),
            ("订单创建", "新订单 #12345 已创建"),
            ("支付完成", "订单支付处理完成"),
            ("发货通知", "商品已发货，快递单号：SF123456"),
            ("系统更新", "应用版本更新至 v2.1.0"),
            ("备份完成", "数据库自动备份成功"),
        ]
        
        title, desc = random.choice(events)
        status = random.choice(list(FluentTimelineItem.Status))
        
        self.interactive_timeline.addItem(
            title, 
            desc,
            datetime.now(),
            status
        )
    
    def clear_timeline(self):
        """Clear timeline"""
        self.interactive_timeline.clear()
    
    def toggle_timeline_order(self):
        """Toggle timeline order"""
        current_order = self.interactive_timeline.reverseOrder()
        self.interactive_timeline.setReverseOrder(not current_order)
    
    def on_timeline_item_clicked(self, index):
        """Handle timeline item clicked"""
        print(f"时间线项目 {index} 被点击")


class BreadcrumbDemo(ComponentDemoTab):
    """Demo for breadcrumb component"""
    
    def __init__(self):
        super().__init__(
            "面包屑导航 (Breadcrumb)",
            "层级导航组件，显示当前页面在网站中的位置"
        )
    
    def setup_content(self):
        # Basic breadcrumb
        basic_group = QGroupBox("基本面包屑")
        basic_layout = QVBoxLayout(basic_group)
        
        self.basic_breadcrumb = FluentBreadcrumb()
        self.basic_breadcrumb.setHomeText("首页")
        
        # Add items
        navigation_items = [
            ("产品管理", "products"),
            ("电子产品", "electronics"),
            ("手机", "phones"),
            ("智能手机", "smartphones"),
            ("iPhone 15", "iphone15")
        ]
        
        for text, data in navigation_items:
            self.basic_breadcrumb.addItem(text, data)
        
        self.basic_breadcrumb.item_clicked.connect(self.on_breadcrumb_clicked)
        
        basic_layout.addWidget(QLabel("导航路径:"))
        basic_layout.addWidget(self.basic_breadcrumb)
        
        # Overflow breadcrumb
        overflow_group = QGroupBox("溢出处理")
        overflow_layout = QVBoxLayout(overflow_group)
        
        self.overflow_breadcrumb = FluentBreadcrumb()
        self.overflow_breadcrumb.setMaxItems(4)
        
        # Add many items
        long_path = [
            ("系统管理", "system"),
            ("用户管理", "users"),
            ("权限管理", "permissions"),
            ("角色管理", "roles"),
            ("系统角色", "system_roles"),
            ("管理员角色", "admin_roles"),
            ("超级管理员", "super_admin"),
            ("权限设置", "settings")
        ]
        
        for text, data in long_path:
            self.overflow_breadcrumb.addItem(text, data)
        
        self.overflow_breadcrumb.item_clicked.connect(self.on_breadcrumb_clicked)
        
        overflow_layout.addWidget(QLabel("长路径 (最多显示4级):"))
        overflow_layout.addWidget(self.overflow_breadcrumb)
        
        # Interactive breadcrumb
        interactive_group = QGroupBox("交互式面包屑")
        interactive_layout = QVBoxLayout(interactive_group)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        add_level_btn = FluentButton("添加层级")
        add_level_btn.clicked.connect(self.add_breadcrumb_level)
        
        remove_level_btn = FluentButton("移除层级")
        remove_level_btn.clicked.connect(self.remove_breadcrumb_level)
        
        controls_layout.addWidget(add_level_btn)
        controls_layout.addWidget(remove_level_btn)
        controls_layout.addStretch()
        
        interactive_layout.addLayout(controls_layout)
        
        # Interactive breadcrumb
        self.interactive_breadcrumb = FluentBreadcrumb()
        self.interactive_breadcrumb.setHomeText("工作台")
        self.interactive_breadcrumb.addItem("项目", "projects")
        self.interactive_breadcrumb.item_clicked.connect(self.on_breadcrumb_clicked)
        
        interactive_layout.addWidget(QLabel("当前位置:"))
        interactive_layout.addWidget(self.interactive_breadcrumb)
        
        # Status display
        self.breadcrumb_status = QLabel("点击面包屑项目查看导航")
        interactive_layout.addWidget(self.breadcrumb_status)
        
        # Main layout
        self.content_layout.addWidget(basic_group)
        self.content_layout.addWidget(overflow_group)
        self.content_layout.addWidget(interactive_group)
        
        self.level_counter = 1
    
    def add_breadcrumb_level(self):
        """Add breadcrumb level"""
        self.level_counter += 1
        self.interactive_breadcrumb.addItem(f"子级别 {self.level_counter}", f"level_{self.level_counter}")
    
    def remove_breadcrumb_level(self):
        """Remove last breadcrumb level"""
        items = self.interactive_breadcrumb.items()
        if items:
            self.interactive_breadcrumb.removeItem(len(items) - 1)
            self.level_counter = max(1, self.level_counter - 1)
    
    def on_breadcrumb_clicked(self, index, data):
        """Handle breadcrumb clicked"""
        self.breadcrumb_status.setText(f"点击了索引 {index}，数据: {data}")


class ColorPickerDemo(ComponentDemoTab):
    """Demo for color picker component"""
    
    def __init__(self):
        super().__init__(
            "颜色选择器 (Color Picker)",
            "完整的颜色选择组件，支持颜色轮、RGB滑块、预设颜色和十六进制输入"
        )
    
    def setup_content(self):
        # Main color picker
        picker_group = QGroupBox("颜色选择器")
        picker_layout = QVBoxLayout(picker_group)
        
        self.color_picker = FluentColorPicker()
        self.color_picker.setMaximumWidth(400)
        self.color_picker.color_changed.connect(self.on_color_changed)
        
        picker_layout.addWidget(self.color_picker)
        
        # Color display
        display_group = QGroupBox("颜色显示")
        display_layout = QVBoxLayout(display_group)
        
        self.color_display = QLabel("当前颜色")
        self.color_display.setMinimumHeight(100)
        self.color_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.color_display.setStyleSheet("""
            QLabel {
                background-color: #ff0000;
                border: 2px solid #ccc;
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        self.color_info = QLabel("RGB: (255, 0, 0)\nHEX: #FF0000")
        self.color_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        display_layout.addWidget(self.color_display)
        display_layout.addWidget(self.color_info)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(picker_group)
        main_layout.addWidget(display_group)
        
        self.content_layout.addLayout(main_layout)
        
        # Initialize with red color
        self.color_picker.setColor(QColor(255, 0, 0))
    
    def on_color_changed(self, color):
        """Handle color change"""
        # Update color display
        self.color_display.setStyleSheet(f"""
            QLabel {{
                background-color: {color.name()};
                border: 2px solid #ccc;
                border-radius: 8px;
                color: {'white' if color.lightness() < 128 else 'black'};
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        
        # Update color info
        self.color_info.setText(f"RGB: ({color.red()}, {color.green()}, {color.blue()})\nHEX: {color.name().upper()}")


class NewComponentsDemo(QMainWindow):
    """Main demo window for new components"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent UI - 新增组件演示")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        
        # Apply theme
        theme_manager.apply_theme(self)
    
    def setup_ui(self):
        """Setup UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("Fluent UI 新增组件演示")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Add demo tabs
        self.tab_widget.addTab(AccordionDemo(), "手风琴")
        self.tab_widget.addTab(DividerDemo(), "分隔线")
        self.tab_widget.addTab(AvatarDemo(), "头像")
        self.tab_widget.addTab(TimelineDemo(), "时间线")
        self.tab_widget.addTab(BreadcrumbDemo(), "面包屑")
        self.tab_widget.addTab(ColorPickerDemo(), "颜色选择器")
        
        layout.addWidget(self.tab_widget)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent UI New Components Demo")
    app.setApplicationVersion("1.0.0")
    
    # Initialize theme
    theme_manager.initialize()
    
    # Create and show main window
    window = NewComponentsDemo()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
