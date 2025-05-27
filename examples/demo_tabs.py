#!/usr/bin/env python3
"""
Additional Demo Tabs for Comprehensive Fluent UI Component Showcase

This module contains the remaining demo tabs for:
- Tree and Hierarchical Components
- Layout and Container Components  
- Media and Content Components
- Command Interface Components
"""

import sys
import os
from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QLabel, 
    QPushButton, QTextEdit, QSpinBox, QCheckBox, QLineEdit,
    QComboBox, QSlider, QProgressBar, QTreeWidgetItem
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QPixmap

# Import component modules
from components.data.tree import (
    FluentTreeWidget, FluentHierarchicalView, FluentOrgChart
)
from components.layout.containers import (
    FluentCard, FluentExpander, FluentSplitter, FluentTabWidget,
    FluentInfoBar, FluentPivot
)
from components.media.players import (
    FluentImageViewer, FluentMediaPlayer, FluentRichContentViewer,
    FluentThumbnailGallery
)
from components.command.bars import (
    FluentCommandBar, FluentToolbar, FluentRibbon,
    FluentQuickAccessToolbar
)

# Import base class
from examples.comprehensive_demo import ComponentDemoTab


class TreeHierarchyDemo(ComponentDemoTab):
    """Demo for tree and hierarchical components"""
    
    def __init__(self):
        super().__init__(
            "树形和层次结构组件",
            "展示树形控件、层次视图和组织架构图等用于显示层次结构数据的组件"
        )
    
    def setup_content(self):
        # Tree Widget Demo
        tree_group = QGroupBox("树形控件 (Tree Widget)")
        tree_layout = QVBoxLayout(tree_group)
        
        self.tree_widget = FluentTreeWidget()
        self.tree_widget.setMinimumHeight(200)
        
        # Add sample tree data
        self.populate_tree()
        
        tree_controls = QHBoxLayout()
        expand_btn = QPushButton("展开全部")
        collapse_btn = QPushButton("折叠全部")
        add_btn = QPushButton("添加项目")
        
        expand_btn.clicked.connect(self.tree_widget.expandAll)
        collapse_btn.clicked.connect(self.tree_widget.collapseAll)
        add_btn.clicked.connect(self.add_tree_item)
        
        tree_controls.addWidget(expand_btn)
        tree_controls.addWidget(collapse_btn)
        tree_controls.addWidget(add_btn)
        tree_controls.addStretch()
        
        tree_layout.addWidget(self.tree_widget)
        tree_layout.addLayout(tree_controls)
        
        # Hierarchical View Demo
        hierarchy_group = QGroupBox("层次视图 (Hierarchical View)")
        hierarchy_layout = QVBoxLayout(hierarchy_group)
        
        self.hierarchy_view = FluentHierarchicalView()
        self.hierarchy_view.setMinimumHeight(250)
        
        # Set sample hierarchical data
        hierarchy_data = {
            "name": "公司总部",
            "type": "company",
            "children": [
                {
                    "name": "技术部门",
                    "type": "department",
                    "children": [
                        {"name": "前端团队", "type": "team"},
                        {"name": "后端团队", "type": "team"},
                        {"name": "测试团队", "type": "team"}
                    ]
                },
                {
                    "name": "产品部门",
                    "type": "department", 
                    "children": [
                        {"name": "产品经理", "type": "team"},
                        {"name": "设计师", "type": "team"}
                    ]
                }
            ]
        }
        self.hierarchy_view.setData(hierarchy_data)
        
        hierarchy_layout.addWidget(self.hierarchy_view)
        
        # Org Chart Demo
        org_chart_group = QGroupBox("组织架构图 (Organization Chart)")
        org_chart_layout = QVBoxLayout(org_chart_group)
        
        self.org_chart = FluentOrgChart()
        self.org_chart.setMinimumHeight(300)
        
        # Set sample org chart data
        org_data = {
            "name": "CEO\n张总",
            "title": "首席执行官",
            "children": [
                {
                    "name": "CTO\n李总",
                    "title": "首席技术官",
                    "children": [
                        {"name": "开发经理\n王经理", "title": "开发部门负责人"},
                        {"name": "运维经理\n赵经理", "title": "运维部门负责人"}
                    ]
                },
                {
                    "name": "CFO\n陈总",
                    "title": "首席财务官",
                    "children": [
                        {"name": "会计主管\n刘主管", "title": "财务部门负责人"}
                    ]
                }
            ]
        }
        self.org_chart.setData(org_data)
        
        org_chart_layout.addWidget(self.org_chart)
        
        # Layout arrangement
        main_layout = QHBoxLayout()
        left_column = QVBoxLayout()
        left_column.addWidget(tree_group)
        left_column.addWidget(hierarchy_group)
        
        main_layout.addLayout(left_column)
        main_layout.addWidget(org_chart_group)
        
        self.content_layout.addLayout(main_layout)
        self.content_layout.addStretch()
    
    def populate_tree(self):
        """Populate tree with sample data"""
        # Create root items
        project_item = QTreeWidgetItem(["项目管理"])
        documents_item = QTreeWidgetItem(["文档库"])
        resources_item = QTreeWidgetItem(["资源"])
        
        # Add children to project item
        project_item.addChild(QTreeWidgetItem(["前端开发"]))
        project_item.addChild(QTreeWidgetItem(["后端开发"]))
        project_item.addChild(QTreeWidgetItem(["数据库设计"]))
        project_item.addChild(QTreeWidgetItem(["测试计划"]))
        
        # Add children to documents item
        docs_tech = QTreeWidgetItem(["技术文档"])
        docs_tech.addChild(QTreeWidgetItem(["API文档"]))
        docs_tech.addChild(QTreeWidgetItem(["架构设计"]))
        docs_tech.addChild(QTreeWidgetItem(["部署指南"]))
        
        docs_user = QTreeWidgetItem(["用户文档"])
        docs_user.addChild(QTreeWidgetItem(["用户手册"]))
        docs_user.addChild(QTreeWidgetItem(["快速入门"]))
        
        documents_item.addChild(docs_tech)
        documents_item.addChild(docs_user)
        
        # Add children to resources item
        resources_item.addChild(QTreeWidgetItem(["图片素材"]))
        resources_item.addChild(QTreeWidgetItem(["字体文件"]))
        resources_item.addChild(QTreeWidgetItem(["图标库"]))
        
        # Add all items to tree
        self.tree_widget.addTopLevelItem(project_item)
        self.tree_widget.addTopLevelItem(documents_item)
        self.tree_widget.addTopLevelItem(resources_item)
        
        # Expand the first item
        project_item.setExpanded(True)
    
    def add_tree_item(self):
        """Add a new item to the tree"""
        current = self.tree_widget.currentItem()
        if current:
            new_item = QTreeWidgetItem([f"新项目 {len(current.children()) + 1}"])
            current.addChild(new_item)
            current.setExpanded(True)


class LayoutContainerDemo(ComponentDemoTab):
    """Demo for layout and container components"""
    
    def __init__(self):
        super().__init__(
            "布局和容器组件",
            "展示卡片、展开器、分割器、标签页等用于组织和布局内容的容器组件"
        )
    
    def setup_content(self):
        # Cards Demo
        cards_group = QGroupBox("卡片 (Cards)")
        cards_layout = QHBoxLayout(cards_group)
        
        # Basic card
        basic_card = FluentCard()
        basic_card.setTitle("基础卡片")
        basic_card.setContent("这是一个基础卡片的示例，展示了卡片的基本外观和功能。")
        basic_card.setMinimumSize(200, 150)
        
        # Clickable card
        clickable_card = FluentCard()
        clickable_card.setTitle("可点击卡片")
        clickable_card.setContent("这个卡片是可点击的，点击时会有交互效果。")
        clickable_card.setClickable(True)
        clickable_card.setMinimumSize(200, 150)
        clickable_card.clicked.connect(lambda: self.show_message("卡片被点击了！"))
        
        # Elevated card
        elevated_card = FluentCard()
        elevated_card.setTitle("高程卡片")
        elevated_card.setContent("这个卡片具有阴影效果，创造出高程感。")
        elevated_card.setElevation(8)
        elevated_card.setMinimumSize(200, 150)
        
        cards_layout.addWidget(basic_card)
        cards_layout.addWidget(clickable_card)
        cards_layout.addWidget(elevated_card)
        cards_layout.addStretch()
        
        # Expander Demo
        expander_group = QGroupBox("展开器 (Expanders)")
        expander_layout = QVBoxLayout(expander_group)
        
        expander1 = FluentExpander()
        expander1.setTitle("设置选项")
        expander1_content = QWidget()
        expander1_content_layout = QVBoxLayout(expander1_content)
        expander1_content_layout.addWidget(QCheckBox("启用通知"))
        expander1_content_layout.addWidget(QCheckBox("自动保存"))
        expander1_content_layout.addWidget(QCheckBox("暗色主题"))
        expander1.setContent(expander1_content)
        
        expander2 = FluentExpander()
        expander2.setTitle("高级配置")
        expander2_content = QWidget()
        expander2_content_layout = QVBoxLayout(expander2_content)
        expander2_content_layout.addWidget(QLabel("缓存大小:"))
        expander2_content_layout.addWidget(QSlider(Qt.Horizontal))
        expander2_content_layout.addWidget(QLabel("网络超时:"))
        expander2_content_layout.addWidget(QSpinBox())
        expander2.setContent(expander2_content)
        
        expander_layout.addWidget(expander1)
        expander_layout.addWidget(expander2)
        
        # Splitter Demo
        splitter_group = QGroupBox("分割器 (Splitter)")
        splitter_layout = QVBoxLayout(splitter_group)
        
        splitter = FluentSplitter(Qt.Horizontal)
        
        left_panel = QTextEdit()
        left_panel.setPlainText("左侧面板\n这里可以放置导航或其他内容...")
        
        right_panel = QTextEdit()
        right_panel.setPlainText("右侧面板\n这里是主要内容区域...")
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])
        
        splitter_layout.addWidget(splitter)
        
        # Info Bar Demo
        info_bar_group = QGroupBox("信息栏 (Info Bars)")
        info_bar_layout = QVBoxLayout(info_bar_group)
        
        info_bar = FluentInfoBar("info")
        info_bar.setTitle("信息")
        info_bar.setMessage("这是一个信息提示栏")
        info_bar.setClosable(True)
        
        warning_bar = FluentInfoBar("warning")
        warning_bar.setTitle("警告")
        warning_bar.setMessage("这是一个警告信息栏")
        warning_bar.setClosable(True)
        
        success_bar = FluentInfoBar("success")
        success_bar.setTitle("成功")
        success_bar.setMessage("操作已成功完成")
        success_bar.setClosable(True)
        
        info_bar_layout.addWidget(info_bar)
        info_bar_layout.addWidget(warning_bar)
        info_bar_layout.addWidget(success_bar)
        
        # Layout arrangement
        top_row = QHBoxLayout()
        top_row.addWidget(cards_group)
        
        middle_row = QHBoxLayout()
        middle_row.addWidget(expander_group)
        middle_row.addWidget(splitter_group)
        
        self.content_layout.addLayout(top_row)
        self.content_layout.addLayout(middle_row)
        self.content_layout.addWidget(info_bar_group)
        self.content_layout.addStretch()
    
    def show_message(self, message):
        """Show a simple message"""
        # This would typically show a notification
        print(f"消息: {message}")


class MediaContentDemo(ComponentDemoTab):
    """Demo for media and content components"""
    
    def __init__(self):
        super().__init__(
            "媒体和内容组件",
            "展示图片查看器、媒体播放器、富内容查看器和缩略图库等媒体相关组件"
        )
    
    def setup_content(self):
        # Image Viewer Demo
        image_group = QGroupBox("图片查看器 (Image Viewer)")
        image_layout = QVBoxLayout(image_group)
        
        self.image_viewer = FluentImageViewer()
        self.image_viewer.setMinimumHeight(250)
        
        image_controls = QHBoxLayout()
        load_btn = QPushButton("加载图片")
        zoom_in_btn = QPushButton("放大")
        zoom_out_btn = QPushButton("缩小")
        fit_btn = QPushButton("适应窗口")
        
        load_btn.clicked.connect(self.load_image)
        zoom_in_btn.clicked.connect(lambda: self.image_viewer.zoomIn())
        zoom_out_btn.clicked.connect(lambda: self.image_viewer.zoomOut())
        fit_btn.clicked.connect(lambda: self.image_viewer.fitToWindow())
        
        image_controls.addWidget(load_btn)
        image_controls.addWidget(zoom_in_btn)
        image_controls.addWidget(zoom_out_btn)
        image_controls.addWidget(fit_btn)
        image_controls.addStretch()
        
        image_layout.addWidget(self.image_viewer)
        image_layout.addLayout(image_controls)
        
        # Rich Content Viewer Demo
        content_group = QGroupBox("富内容查看器 (Rich Content Viewer)")
        content_layout = QVBoxLayout(content_group)
        
        self.content_viewer = FluentRichContentViewer()
        self.content_viewer.setMinimumHeight(250)
        
        # Set sample content
        sample_html = """
        <h2>欢迎使用富内容查看器</h2>
        <p>这个组件可以显示 <strong>HTML</strong> 和 <em>Markdown</em> 内容。</p>
        <ul>
            <li>支持文本格式化</li>
            <li>支持列表和表格</li>
            <li>支持链接和图片</li>
        </ul>
        <p>这是一个 <a href="https://example.com">示例链接</a>。</p>
        """
        self.content_viewer.setContent(sample_html, "html")
        
        content_controls = QHBoxLayout()
        html_btn = QPushButton("HTML 模式")
        markdown_btn = QPushButton("Markdown 模式")
        
        html_btn.clicked.connect(lambda: self.set_content_mode("html"))
        markdown_btn.clicked.connect(lambda: self.set_content_mode("markdown"))
        
        content_controls.addWidget(html_btn)
        content_controls.addWidget(markdown_btn)
        content_controls.addStretch()
        
        content_layout.addWidget(self.content_viewer)
        content_layout.addLayout(content_controls)
        
        # Media Player Demo
        media_group = QGroupBox("媒体播放器 (Media Player)")
        media_layout = QVBoxLayout(media_group)
        
        self.media_player = FluentMediaPlayer()
        self.media_player.setMinimumHeight(200)
        
        media_controls = QHBoxLayout()
        load_media_btn = QPushButton("加载媒体")
        play_btn = QPushButton("播放")
        pause_btn = QPushButton("暂停")
        stop_btn = QPushButton("停止")
        
        load_media_btn.clicked.connect(self.load_media)
        play_btn.clicked.connect(lambda: self.media_player.play())
        pause_btn.clicked.connect(lambda: self.media_player.pause())
        stop_btn.clicked.connect(lambda: self.media_player.stop())
        
        media_controls.addWidget(load_media_btn)
        media_controls.addWidget(play_btn)
        media_controls.addWidget(pause_btn)
        media_controls.addWidget(stop_btn)
        media_controls.addStretch()
        
        media_layout.addWidget(self.media_player)
        media_layout.addLayout(media_controls)
        
        # Thumbnail Gallery Demo
        gallery_group = QGroupBox("缩略图库 (Thumbnail Gallery)")
        gallery_layout = QVBoxLayout(gallery_group)
        
        self.thumbnail_gallery = FluentThumbnailGallery()
        self.thumbnail_gallery.setMinimumHeight(200)
        self.thumbnail_gallery.setThumbnailSize(128, 128)
        
        gallery_controls = QHBoxLayout()
        load_folder_btn = QPushButton("加载文件夹")
        grid_btn = QPushButton("网格视图")
        list_btn = QPushButton("列表视图")
        
        load_folder_btn.clicked.connect(self.load_gallery_folder)
        grid_btn.clicked.connect(lambda: self.thumbnail_gallery.setViewMode("grid"))
        list_btn.clicked.connect(lambda: self.thumbnail_gallery.setViewMode("list"))
        
        gallery_controls.addWidget(load_folder_btn)
        gallery_controls.addWidget(grid_btn)
        gallery_controls.addWidget(list_btn)
        gallery_controls.addStretch()
        
        gallery_layout.addWidget(self.thumbnail_gallery)
        gallery_layout.addLayout(gallery_controls)
        
        # Layout arrangement
        left_column = QVBoxLayout()
        left_column.addWidget(image_group)
        left_column.addWidget(content_group)
        
        right_column = QVBoxLayout()
        right_column.addWidget(media_group)
        right_column.addWidget(gallery_group)
        
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_column)
        main_layout.addLayout(right_column)
        
        self.content_layout.addLayout(main_layout)
        self.content_layout.addStretch()
    
    def load_image(self):
        """Load an image file"""
        # In a real application, this would open a file dialog
        print("加载图片功能 - 在实际应用中会打开文件对话框")
    
    def load_media(self):
        """Load a media file"""
        # In a real application, this would open a file dialog
        print("加载媒体功能 - 在实际应用中会打开文件对话框")
    
    def load_gallery_folder(self):
        """Load a folder for thumbnail gallery"""
        # In a real application, this would open a folder dialog
        print("加载文件夹功能 - 在实际应用中会打开文件夹对话框")
    
    def set_content_mode(self, mode):
        """Set content viewer mode"""
        if mode == "html":
            sample_html = """
            <h2>HTML 内容示例</h2>
            <p>这是 <strong>HTML</strong> 格式的内容。</p>
            <table border="1">
                <tr><th>功能</th><th>状态</th></tr>
                <tr><td>HTML 渲染</td><td>✓ 支持</td></tr>
                <tr><td>CSS 样式</td><td>✓ 支持</td></tr>
            </table>
            """
            self.content_viewer.setContent(sample_html, "html")
        else:
            sample_markdown = """
# Markdown 内容示例

这是 **Markdown** 格式的内容。

## 功能列表

- [x] 文本格式化
- [x] 列表支持
- [ ] 图片支持
- [ ] 代码高亮

> 这是一个引用块示例
            """
            self.content_viewer.setContent(sample_markdown, "markdown")


class CommandInterfaceDemo(ComponentDemoTab):
    """Demo for command interface components"""
    
    def __init__(self):
        super().__init__(
            "命令界面组件",
            "展示命令栏、工具栏、功能区和快速访问工具栏等用户界面命令组件"
        )
    
    def setup_content(self):
        # Command Bar Demo
        command_bar_group = QGroupBox("命令栏 (Command Bar)")
        command_bar_layout = QVBoxLayout(command_bar_group)
        
        self.command_bar = FluentCommandBar()
        
        # Add primary commands
        self.command_bar.addPrimaryCommand("new", "新建", "创建新文档")
        self.command_bar.addPrimaryCommand("open", "打开", "打开现有文档")
        self.command_bar.addPrimaryCommand("save", "保存", "保存当前文档")
        
        # Add secondary commands
        self.command_bar.addSecondaryCommand("print", "打印", "打印文档")
        self.command_bar.addSecondaryCommand("export", "导出", "导出文档")
        self.command_bar.addSecondaryCommand("share", "分享", "分享文档")
        
        command_bar_layout.addWidget(self.command_bar)
        
        # Toolbar Demo
        toolbar_group = QGroupBox("工具栏 (Toolbar)")
        toolbar_layout = QVBoxLayout(toolbar_group)
        
        self.toolbar = FluentToolbar()
        
        # Add toolbar items
        self.toolbar.addAction("cut", "剪切", "剪切选中内容")
        self.toolbar.addAction("copy", "复制", "复制选中内容")
        self.toolbar.addAction("paste", "粘贴", "粘贴内容")
        self.toolbar.addSeparator()
        self.toolbar.addAction("undo", "撤销", "撤销上一步操作")
        self.toolbar.addAction("redo", "重做", "重做操作")
        
        # Add toggle group
        self.toolbar.addToggleGroup("format", [
            ("bold", "粗体", "设置文本为粗体"),
            ("italic", "斜体", "设置文本为斜体"),
            ("underline", "下划线", "添加下划线")
        ])
        
        toolbar_layout.addWidget(self.toolbar)
        
        # Ribbon Demo
        ribbon_group = QGroupBox("功能区 (Ribbon)")
        ribbon_layout = QVBoxLayout(ribbon_group)
        
        self.ribbon = FluentRibbon()
        
        # Create Home tab
        home_tab = self.ribbon.addTab("home", "开始")
        
        # Add clipboard group
        clipboard_group = home_tab.addGroup("clipboard", "剪贴板")
        clipboard_group.addLargeCommand("paste", "粘贴", "粘贴内容")
        clipboard_group.addSmallCommand("cut", "剪切", "剪切选中内容")
        clipboard_group.addSmallCommand("copy", "复制", "复制选中内容")
        
        # Add font group
        font_group = home_tab.addGroup("font", "字体")
        font_group.addComboBox("font_family", ["宋体", "黑体", "微软雅黑"])
        font_group.addSpinBox("font_size", 12, 1, 72)
        font_group.addSmallCommand("bold", "粗体", "设置粗体")
        font_group.addSmallCommand("italic", "斜体", "设置斜体")
        
        # Create Insert tab
        insert_tab = self.ribbon.addTab("insert", "插入")
        
        # Add tables group
        tables_group = insert_tab.addGroup("tables", "表格")
        tables_group.addLargeCommand("table", "表格", "插入表格")
        
        # Add illustrations group
        illustrations_group = insert_tab.addGroup("illustrations", "插图")
        illustrations_group.addLargeCommand("picture", "图片", "插入图片")
        illustrations_group.addLargeCommand("shapes", "形状", "插入形状")
        illustrations_group.addLargeCommand("chart", "图表", "插入图表")
        
        ribbon_layout.addWidget(self.ribbon)
        
        # Quick Access Toolbar Demo
        quick_access_group = QGroupBox("快速访问工具栏 (Quick Access Toolbar)")
        quick_access_layout = QVBoxLayout(quick_access_group)
        
        self.quick_access = FluentQuickAccessToolbar()
        self.quick_access.addAction("save", "保存", "快速保存")
        self.quick_access.addAction("undo", "撤销", "快速撤销")
        self.quick_access.addAction("redo", "重做", "快速重做")
        
        quick_access_layout.addWidget(self.quick_access)
        
        # Layout arrangement
        self.content_layout.addWidget(command_bar_group)
        self.content_layout.addWidget(toolbar_group)
        self.content_layout.addWidget(ribbon_group)
        self.content_layout.addWidget(quick_access_group)
        self.content_layout.addStretch()
