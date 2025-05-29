"""
Enhanced Components Demo
Showcases the improved components with better animations and reusability
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QHBoxLayout, QWidget, QLabel, QFrame, 
                               QScrollArea, QTextEdit, QCheckBox, QSpinBox,
                               QLineEdit, QComboBox, QSlider)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor

from core.theme import theme_manager
from core.enhanced_base import FluentLayoutBuilder
from components.basic.button_enhanced import (FluentButtonEnhanced, 
                                            FluentIconButtonEnhanced, 
                                            FluentToggleButtonEnhanced)
from components.composite import (FluentActionToolbar, FluentSearchToolbar, 
                                FluentViewToolbar, FluentStatusToolbar,
                                FluentSettingsPanel, FluentFormDialog,
                                FluentSidebar, FluentHeaderNavigation)


class EnhancedComponentsDemo(QMainWindow):
    """Demo showcasing enhanced components with improved code quality"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Fluent Components Demo")
        self.setGeometry(100, 100, 1200, 800)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the enhanced UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Use enhanced layout builder
        main_layout = FluentLayoutBuilder.create_horizontal_layout(margins=(0, 0, 0, 0))
        central_widget.setLayout(main_layout)
        
        # Create enhanced sidebar
        self._create_sidebar(main_layout)
        
        # Create main content area
        self._create_main_content(main_layout)
        
        # Setup theme
        self._apply_theme()
    
    def _create_sidebar(self, parent_layout):
        """Create enhanced sidebar with composite components"""
        sidebar = FluentSidebar("导航菜单", self)
        sidebar.setFixedWidth(250)
        
        # Add navigation sections
        sections = [
            {
                'title': '组件展示',
                'items': [
                    {'text': '增强按钮', 'id': 'buttons'},
                    {'text': '工具栏组件', 'id': 'toolbars'},
                    {'text': '表单组件', 'id': 'forms'},
                    {'text': '面板组件', 'id': 'panels'}
                ]
            },
            {
                'title': '动画效果',
                'items': [
                    {'text': '微交互', 'id': 'micro_interactions'},
                    {'text': '过渡动画', 'id': 'transitions'},
                    {'text': '状态变化', 'id': 'state_changes'}
                ]
            }
        ]
        
        for section in sections:
            sidebar.add_section(section['title'], section['items'])
        
        # Connect navigation
        sidebar.item_clicked.connect(self._on_sidebar_navigation)
        
        parent_layout.addWidget(sidebar)
    
    def _create_main_content(self, parent_layout):
        """Create main content area with toolbars"""
        main_container = QWidget()
        main_layout = FluentLayoutBuilder.create_vertical_layout(margins=(0, 0, 0, 0))
        main_container.setLayout(main_layout)
        
        # Create header navigation
        header_nav = FluentHeaderNavigation("Enhanced Components", self)
        header_nav.add_breadcrumb("首页")
        header_nav.add_breadcrumb("组件库")
        header_nav.add_breadcrumb("增强组件")
        main_layout.addWidget(header_nav)
        
        # Create action toolbar
        action_toolbar = self._create_action_toolbar()
        main_layout.addWidget(action_toolbar)
        
        # Create search toolbar
        search_toolbar = self._create_search_toolbar()
        main_layout.addWidget(search_toolbar)
        
        # Create view toolbar
        view_toolbar = self._create_view_toolbar()
        main_layout.addWidget(view_toolbar)
        
        # Create scrollable content area
        scroll_area, content_layout = FluentLayoutBuilder.create_content_area(scrollable=True)
        main_layout.addWidget(scroll_area)
        
        # Add demo content
        self._create_demo_content(content_layout)
        
        # Create status toolbar
        status_toolbar = self._create_status_toolbar()
        main_layout.addWidget(status_toolbar)
        
        parent_layout.addWidget(main_container)
    
    def _create_action_toolbar(self):
        """Create enhanced action toolbar"""
        toolbar = FluentActionToolbar("操作工具栏")
        
        # File actions
        file_actions = [
            {'id': 'new', 'text': '新建', 'tooltip': '创建新文件', 'callback': self._on_new_file},
            {'id': 'open', 'text': '打开', 'tooltip': '打开文件', 'callback': self._on_open_file},
            {'id': 'save', 'text': '保存', 'tooltip': '保存文件', 'callback': self._on_save_file}
        ]
        toolbar.add_action_group('file', file_actions)
        
        # Edit actions
        edit_actions = [
            {'id': 'undo', 'text': '撤销', 'tooltip': '撤销操作', 'callback': self._on_undo},
            {'id': 'redo', 'text': '重做', 'tooltip': '重做操作', 'callback': self._on_redo}
        ]
        toolbar.add_action_group('edit', edit_actions)
        
        # View toggle actions
        view_actions = [
            {'id': 'grid', 'text': '网格', 'tooltip': '网格视图'},
            {'id': 'list', 'text': '列表', 'tooltip': '列表视图'}
        ]
        toolbar.add_toggle_group('view', view_actions, exclusive=True)
        
        return toolbar
    
    def _create_search_toolbar(self):
        """Create enhanced search toolbar"""
        toolbar = FluentSearchToolbar("搜索组件...")
        
        # Add filter options
        category_options = [
            ('全部类别', 'all'),
            ('按钮组件', 'buttons'), 
            ('表单组件', 'forms'),
            ('面板组件', 'panels')
        ]
        toolbar.add_filter_combo('category', '类别:', category_options)
        
        status_options = [
            ('全部状态', 'all'),
            ('稳定版', 'stable'),
            ('测试版', 'beta'),
            ('实验性', 'experimental')
        ]
        toolbar.add_filter_combo('status', '状态:', status_options)
        
        # Add view controls
        view_modes = [
            {'id': 'card', 'tooltip': '卡片视图'},
            {'id': 'list', 'tooltip': '列表视图'},
            {'id': 'grid', 'tooltip': '网格视图'}
        ]
        toolbar.add_view_controls(view_modes, default='card')
        
        return toolbar
    
    def _create_view_toolbar(self):
        """Create enhanced view toolbar"""
        toolbar = FluentViewToolbar("视图选项")
        
        # Add sort options
        sort_options = [
            ('名称', 'name'),
            ('创建时间', 'created'),
            ('修改时间', 'modified'),
            ('大小', 'size')
        ]
        toolbar.add_sort_options(sort_options)
        
        # Add group options
        group_options = [
            ('类型', 'type'),
            ('状态', 'status'),
            ('标签', 'tag')
        ]
        toolbar.add_group_options(group_options)
        
        return toolbar
    
    def _create_status_toolbar(self):
        """Create enhanced status toolbar"""
        toolbar = FluentStatusToolbar()
        
        # Add statistics
        toolbar.add_stat('components', '组件数量', '25')
        toolbar.add_stat('enhanced', '已增强', '15')
        toolbar.add_stat('errors', '错误', '0')
        
        # Set initial status
        toolbar.set_status("组件加载完成")
        
        return toolbar
    
    def _create_demo_content(self, layout):
        """Create demo content showcasing enhanced components"""
        
        # Enhanced Buttons Section
        self._add_section_title(layout, "增强按钮组件")
        buttons_container = self._create_buttons_demo()
        layout.addWidget(buttons_container)
        
        # Settings Panel Section
        self._add_section_title(layout, "设置面板组件")
        settings_panel = self._create_settings_panel_demo()
        layout.addWidget(settings_panel)
        
        # Form Components Section
        self._add_section_title(layout, "表单组件")
        form_container = self._create_form_demo()
        layout.addWidget(form_container)
        
        # Animation showcase
        self._add_section_title(layout, "动画效果展示")
        animation_container = self._create_animation_demo()
        layout.addWidget(animation_container)
    
    def _add_section_title(self, layout, title):
        """Add section title with enhanced styling"""
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {theme_manager.get_color('text_primary').name()};
                padding: 20px 0 10px 0;
                border-bottom: 2px solid {theme_manager.get_color('primary').name()};
                margin-bottom: 15px;
            }}
        """)
        layout.addWidget(title_label)
    
    def _create_buttons_demo(self):
        """Create enhanced buttons demo"""
        container = QFrame()
        container.setFrameStyle(QFrame.Shape.Box)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {theme_manager.get_color('surface').name()};
                border: 1px solid {theme_manager.get_color('border').name()};
                border-radius: 8px;
                padding: 15px;
                margin: 5px 0;
            }}
        """)
        
        layout = FluentLayoutBuilder.create_vertical_layout(margins=(15, 15, 15, 15))
        container.setLayout(layout)
        
        # Different button styles
        buttons_layout = FluentLayoutBuilder.create_horizontal_layout()
        
        # Primary button
        primary_btn = FluentButtonEnhanced("主要按钮", style=FluentButtonEnhanced.ButtonStyle.PRIMARY)
        buttons_layout.addWidget(primary_btn)
        
        # Secondary button
        secondary_btn = FluentButtonEnhanced("次要按钮", style=FluentButtonEnhanced.ButtonStyle.SECONDARY)
        buttons_layout.addWidget(secondary_btn)
        
        # Accent button
        accent_btn = FluentButtonEnhanced("强调按钮", style=FluentButtonEnhanced.ButtonStyle.ACCENT)
        buttons_layout.addWidget(accent_btn)
        
        # Subtle button
        subtle_btn = FluentButtonEnhanced("微妙按钮", style=FluentButtonEnhanced.ButtonStyle.SUBTLE)
        buttons_layout.addWidget(subtle_btn)
        
        # Outline button
        outline_btn = FluentButtonEnhanced("轮廓按钮", style=FluentButtonEnhanced.ButtonStyle.OUTLINE)
        buttons_layout.addWidget(outline_btn)
        
        # Toggle button
        toggle_btn = FluentToggleButtonEnhanced("切换按钮")
        buttons_layout.addWidget(toggle_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Button with enhanced animations
        description = QLabel("这些按钮使用了增强的动画效果和一致的样式系统。")
        description.setStyleSheet(f"color: {theme_manager.get_color('text_secondary').name()};")
        layout.addWidget(description)
        
        return container
    
    def _create_settings_panel_demo(self):
        """Create settings panel demo"""
        settings_panel = FluentSettingsPanel("应用设置")
        
        # UI Settings
        ui_settings = [
            {'type': 'combo', 'id': 'theme', 'label': '主题', 
             'options': [('浅色', 'light'), ('深色', 'dark'), ('自动', 'auto')], 'value': 'light'},
            {'type': 'combo', 'id': 'language', 'label': '语言', 
             'options': [('中文', 'zh'), ('English', 'en')], 'value': 'zh'},
            {'type': 'checkbox', 'id': 'animations', 'label': '启用动画', 'value': True},
            {'type': 'checkbox', 'id': 'sounds', 'label': '启用声音', 'value': False}
        ]
        settings_panel.add_group("界面设置", ui_settings)
        
        # Performance Settings  
        performance_settings = [
            {'type': 'slider', 'id': 'fps', 'label': '帧率限制', 'range': (30, 120), 'value': 60},
            {'type': 'checkbox', 'id': 'hardware_acceleration', 'label': '硬件加速', 'value': True},
            {'type': 'spin', 'id': 'cache_size', 'label': '缓存大小 (MB)', 'range': (100, 2000), 'value': 500}
        ]
        settings_panel.add_group("性能设置", performance_settings)
        
        return settings_panel
    
    def _create_form_demo(self):
        """Create form components demo"""
        container = QFrame()
        container.setFrameStyle(QFrame.Shape.Box)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {theme_manager.get_color('surface').name()};
                border: 1px solid {theme_manager.get_color('border').name()};
                border-radius: 8px;
                padding: 15px;
                margin: 5px 0;
            }}
        """)
        
        layout = FluentLayoutBuilder.create_vertical_layout(margins=(15, 15, 15, 15))
        container.setLayout(layout)
        
        # Form demonstration
        form_layout = FluentLayoutBuilder.create_grid_layout()
        
        # Name field
        form_layout.addWidget(QLabel("姓名:"), 0, 0)
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("请输入您的姓名")
        form_layout.addWidget(name_edit, 0, 1)
        
        # Email field
        form_layout.addWidget(QLabel("邮箱:"), 1, 0)
        email_edit = QLineEdit()
        email_edit.setPlaceholderText("请输入邮箱地址")
        form_layout.addWidget(email_edit, 1, 1)
        
        # Age field
        form_layout.addWidget(QLabel("年龄:"), 2, 0)
        age_spin = QSpinBox()
        age_spin.setRange(1, 120)
        age_spin.setValue(25)
        form_layout.addWidget(age_spin, 2, 1)
        
        layout.addLayout(form_layout)
        
        # Form actions
        actions_layout = FluentLayoutBuilder.create_horizontal_layout()
        actions_layout.addStretch()
        
        submit_btn = FluentButtonEnhanced("提交", style=FluentButtonEnhanced.ButtonStyle.PRIMARY)
        cancel_btn = FluentButtonEnhanced("取消", style=FluentButtonEnhanced.ButtonStyle.SECONDARY)
        
        actions_layout.addWidget(cancel_btn)
        actions_layout.addWidget(submit_btn)
        layout.addLayout(actions_layout)
        
        return container
    
    def _create_animation_demo(self):
        """Create animation effects demo"""
        container = QFrame()
        container.setFrameStyle(QFrame.Shape.Box)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {theme_manager.get_color('surface').name()};
                border: 1px solid {theme_manager.get_color('border').name()};
                border-radius: 8px;
                padding: 15px;
                margin: 5px 0;
            }}
        """)
        
        layout = FluentLayoutBuilder.create_vertical_layout(margins=(15, 15, 15, 15))
        container.setLayout(layout)
        
        # Animation controls
        controls_layout = FluentLayoutBuilder.create_horizontal_layout()
        
        fade_btn = FluentButtonEnhanced("淡入淡出", style=FluentButtonEnhanced.ButtonStyle.SUBTLE)
        scale_btn = FluentButtonEnhanced("缩放动画", style=FluentButtonEnhanced.ButtonStyle.SUBTLE)
        slide_btn = FluentButtonEnhanced("滑动动画", style=FluentButtonEnhanced.ButtonStyle.SUBTLE)
        
        controls_layout.addWidget(fade_btn)
        controls_layout.addWidget(scale_btn)
        controls_layout.addWidget(slide_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Animation target
        target_frame = QFrame()
        target_frame.setFixedSize(200, 100)
        target_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme_manager.get_color('accent_light').name()};
                border: 2px solid {theme_manager.get_color('primary').name()};
                border-radius: 8px;
            }}
        """)
        
        target_layout = FluentLayoutBuilder.create_horizontal_layout()
        target_layout.addWidget(target_frame)
        target_layout.addStretch()
        layout.addLayout(target_layout)
        
        return container
    
    def _apply_theme(self):
        """Apply theme to main window"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme_manager.get_color('background').name()};
                color: {theme_manager.get_color('text_primary').name()};
            }}
        """)
    
    # Event handlers
    def _on_sidebar_navigation(self, item_id: str):
        """Handle sidebar navigation"""
        print(f"导航到: {item_id}")
    
    def _on_new_file(self):
        """Handle new file action"""
        print("新建文件")
    
    def _on_open_file(self):
        """Handle open file action"""
        print("打开文件")
    
    def _on_save_file(self):
        """Handle save file action"""
        print("保存文件")
    
    def _on_undo(self):
        """Handle undo action"""
        print("撤销操作")
    
    def _on_redo(self):
        """Handle redo action"""
        print("重做操作")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show demo
    demo = EnhancedComponentsDemo()
    demo.show()
    
    sys.exit(app.exec())
