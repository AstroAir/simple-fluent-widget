#!/usr/bin/env python3
"""
Comprehensive Demo Application for Fluent UI Components

This demo showcases all the advanced Fluent UI components including:
- Data Visualization Components (charts, progress)
- Data Entry Components (forms, inputs, editors)
- Tree and Hierarchical Components
- Status and Notification Components
- Layout and Container Components
- Media and Content Components
- Command Bar and Ribbon Components
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QScrollArea, QTabWidget, QWidget,
    QLabel, QPushButton, QGroupBox, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import all component modules
from components.data import FluentRichTextEditor
from components.data.charts import (
    FluentProgressRing, FluentBarChart, FluentLineChart, FluentPieChart
)
from components.data.entry import (
    FluentMaskedLineEdit, FluentAutoCompleteEdit, FluentRichTextEditor,
    FluentDateTimePicker, FluentSlider, FluentFileSelector
)
from components.data.status import (
    FluentStatusIndicator, FluentProgressTracker, FluentNotification,
    FluentNotificationManager, FluentBadge
)


class ComponentDemoTab(QWidget):
    """Base class for component demonstration tabs"""
    
    def __init__(self, title: str, description: str):
        super().__init__()
        self.title = title
        self.description = description
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title and description
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        
        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.content_layout = QVBoxLayout(scroll_widget)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        self.setup_content()
    
    def setup_content(self):
        """Override in subclasses to add specific content"""
        pass


class DataVisualizationDemo(ComponentDemoTab):
    """Demo for data visualization components"""
    
    def __init__(self):
        super().__init__(
            "数据可视化组件",
            "展示进度环、柱状图、折线图和饼图等数据可视化组件的功能"
        )
    
    def setup_content(self):
        # Progress Ring Demo
        progress_group = QGroupBox("进度环 (Progress Ring)")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_ring = FluentProgressRing()
        self.progress_ring.setMaximumSize(200, 200)
        self.progress_ring.setValue(65)
        
        progress_controls = QHBoxLayout()
        progress_spin = QSpinBox()
        progress_spin.setRange(0, 100)
        progress_spin.setValue(65)
        progress_spin.valueChanged.connect(self.update_progress)
        
        progress_controls.addWidget(QLabel("进度值:"))
        progress_controls.addWidget(progress_spin)
        progress_controls.addStretch()
        
        progress_layout.addWidget(self.progress_ring)
        progress_layout.addLayout(progress_controls)
        
        # Bar Chart Demo
        bar_chart_group = QGroupBox("柱状图 (Bar Chart)")
        bar_chart_layout = QVBoxLayout(bar_chart_group)
        self.bar_chart = FluentBarChart()
        self.bar_chart.setMinimumHeight(250)
        chart_data = [
            ("Q1", 120, QColor("#0078d4")),
            ("Q2", 180, QColor("#106ebe")),
            ("Q3", 95, QColor("#005a9e")),
            ("Q4", 205, QColor("#004578"))
        ]
        self.bar_chart.setData(chart_data)
        
        bar_chart_layout.addWidget(self.bar_chart)
        
        # Line Chart Demo
        line_chart_group = QGroupBox("折线图 (Line Chart)")
        line_chart_layout = QVBoxLayout(line_chart_group)
        self.line_chart = FluentLineChart()
        self.line_chart.setMinimumHeight(250)
        line_data = [
            (1, 30), (2, 45), (3, 35),
            (4, 55), (5, 40), (6, 65)
        ]
        self.line_chart.addSeries("Series 1", line_data)
        
        line_chart_layout.addWidget(self.line_chart)
        
        # Pie Chart Demo
        pie_chart_group = QGroupBox("饼图 (Pie Chart)")
        pie_chart_layout = QVBoxLayout(pie_chart_group)
        self.pie_chart = FluentPieChart()
        self.pie_chart.setMinimumHeight(250)
        pie_data = [
            ("Windows", 45.2, QColor("#0078d4")),
            ("macOS", 15.8, QColor("#00bcf2")),
            ("Linux", 12.3, QColor("#40e0d0")),
            ("Others", 26.7, QColor("#8764b8"))
        ]
        self.pie_chart.setData(pie_data)
        
        pie_chart_layout.addWidget(self.pie_chart)
        
        # Add all groups to layout
        row1 = QHBoxLayout()
        row1.addWidget(progress_group)
        row1.addWidget(bar_chart_group)
        
        row2 = QHBoxLayout()
        row2.addWidget(line_chart_group)
        row2.addWidget(pie_chart_group)
        
        self.content_layout.addLayout(row1)
        self.content_layout.addLayout(row2)
        self.content_layout.addStretch()
    
    def update_progress(self, value):
        self.progress_ring.setValue(value)


class DataEntryDemo(ComponentDemoTab):
    """Demo for data entry components"""
    
    def __init__(self):
        super().__init__(
            "数据输入组件",
            "展示各种高级输入控件，包括格式化输入、自动完成、富文本编辑器等"
        )
    
    def setup_content(self):
        # Left column
        left_column = QVBoxLayout()
        
        # Masked Input Demo
        masked_group = QGroupBox("格式化输入 (Masked Input)")
        masked_layout = QVBoxLayout(masked_group)
        
        phone_edit = FluentMaskedLineEdit()
        phone_edit.setInputMask("(999) 999-9999")
        phone_edit.setPlaceholderText("电话号码")
        
        date_edit = FluentMaskedLineEdit()
        date_edit.setInputMask("9999/99/99")
        date_edit.setPlaceholderText("日期 (YYYY/MM/DD)")
        
        masked_layout.addWidget(QLabel("电话号码:"))
        masked_layout.addWidget(phone_edit)
        masked_layout.addWidget(QLabel("日期:"))
        masked_layout.addWidget(date_edit)
        
        # Auto Complete Demo
        auto_complete_group = QGroupBox("自动完成 (Auto Complete)")
        auto_complete_layout = QVBoxLayout(auto_complete_group)
        self.auto_complete = FluentAutoCompleteEdit()
        self.auto_complete.setPlaceholderText("输入编程语言...")
        suggestions = [
            "Python", "JavaScript", "TypeScript", "Java", "C#", 
            "C++", "Go", "Rust", "Swift", "Kotlin"
        ]
        for suggestion in suggestions:
            self.auto_complete.addSuggestion(suggestion)
        
        auto_complete_layout.addWidget(self.auto_complete)
          # Date Time Picker Demo
        datetime_group = QGroupBox("日期时间选择器 (DateTime Picker)")
        datetime_layout = QVBoxLayout(datetime_group)
        
        date_picker = FluentDateTimePicker(mode='date')
        time_picker = FluentDateTimePicker(mode='time')
        datetime_picker = FluentDateTimePicker(mode='datetime')
        
        datetime_layout.addWidget(QLabel("仅日期:"))
        datetime_layout.addWidget(date_picker)
        datetime_layout.addWidget(QLabel("仅时间:"))
        datetime_layout.addWidget(time_picker)
        datetime_layout.addWidget(QLabel("日期时间:"))
        datetime_layout.addWidget(datetime_picker)
        
        left_column.addWidget(masked_group)
        left_column.addWidget(auto_complete_group)
        left_column.addWidget(datetime_group)
        
        # Right column
        right_column = QVBoxLayout()
        
        # Rich Text Editor Demo
        editor_group = QGroupBox("富文本编辑器 (Rich Text Editor)")
        editor_layout = QVBoxLayout(editor_group)
        
        self.rich_editor = FluentRichTextEditor()
        self.rich_editor.setMinimumHeight(200)
        self.rich_editor.setPlainText("这是一个富文本编辑器的示例文本。\n您可以使用工具栏来格式化文本。")
        
        editor_layout.addWidget(self.rich_editor)
        
        # Slider Demo
        slider_group = QGroupBox("滑块 (Slider)")
        slider_layout = QVBoxLayout(slider_group)
        
        h_slider = FluentSlider(Qt.Orientation.Horizontal)
        h_slider.setRange(0, 100)
        h_slider.setValue(50)
        h_slider.setValueVisible(True)
        
        v_slider = FluentSlider(Qt.Orientation.Vertical)
        v_slider.setRange(0, 100)
        v_slider.setValue(30)
        v_slider.setValueVisible(True)
        
        slider_h_layout = QHBoxLayout()
        slider_h_layout.addWidget(QLabel("水平滑块:"))
        slider_h_layout.addWidget(h_slider)
        
        slider_v_layout = QHBoxLayout()
        slider_v_layout.addWidget(QLabel("垂直滑块:"))
        slider_v_layout.addWidget(v_slider)
        slider_v_layout.addStretch()
        
        slider_layout.addLayout(slider_h_layout)
        slider_layout.addLayout(slider_v_layout)
        
        # File Selector Demo
        file_group = QGroupBox("文件选择器 (File Selector)")
        file_layout = QVBoxLayout(file_group)
        
        single_file = FluentFileSelector(multi_select=False)
        single_file.setFileTypes(["*.py", "*.txt", "*.md"])
        
        multi_file = FluentFileSelector(multi_select=True)
        multi_file.setFileTypes(["*.jpg", "*.png", "*.gif", "*.bmp"])
        
        file_layout.addWidget(QLabel("单文件选择:"))
        file_layout.addWidget(single_file)
        file_layout.addWidget(QLabel("多文件选择:"))
        file_layout.addWidget(multi_file)
        
        right_column.addWidget(editor_group)
        right_column.addWidget(slider_group)
        right_column.addWidget(file_group)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_column)
        main_layout.addLayout(right_column)
        
        self.content_layout.addLayout(main_layout)
        self.content_layout.addStretch()


class StatusNotificationDemo(ComponentDemoTab):
    """Demo for status and notification components"""
    
    def __init__(self):
        super().__init__(
            "状态和通知组件",
            "展示状态指示器、进度跟踪器、通知系统和徽章组件"
        )
    
    def setup_content(self):
        # Status Indicators Demo
        status_group = QGroupBox("状态指示器 (Status Indicators)")
        status_layout = QVBoxLayout(status_group)
        
        indicators_layout = QHBoxLayout()
        
        success_indicator = FluentStatusIndicator("success")
        success_indicator.setLabel("成功")
        success_indicator.setAnimationEnabled(True)
        
        warning_indicator = FluentStatusIndicator("warning")
        warning_indicator.setLabel("警告")
        warning_indicator.setAnimationEnabled(True)
        
        error_indicator = FluentStatusIndicator("error")
        error_indicator.setLabel("错误")
        error_indicator.setAnimationEnabled(True)
        
        info_indicator = FluentStatusIndicator("info")
        info_indicator.setLabel("信息")
        info_indicator.setAnimationEnabled(True)
        
        indicators_layout.addWidget(success_indicator)
        indicators_layout.addWidget(warning_indicator)
        indicators_layout.addWidget(error_indicator)
        indicators_layout.addWidget(info_indicator)
        indicators_layout.addStretch()
        
        status_layout.addLayout(indicators_layout)
        
        # Progress Tracker Demo
        tracker_group = QGroupBox("进度跟踪器 (Progress Tracker)")
        tracker_layout = QVBoxLayout(tracker_group)
        
        self.progress_tracker = FluentProgressTracker()
        steps = ["开始", "验证", "处理", "确认", "完成"]
        self.progress_tracker.setStepLabels(steps)
        self.progress_tracker.setCurrentStepIndex(2)
        
        tracker_controls = QHBoxLayout()
        prev_btn = QPushButton("上一步")
        next_btn = QPushButton("下一步")
        prev_btn.clicked.connect(self.prev_step)
        next_btn.clicked.connect(self.next_step)
        
        tracker_controls.addWidget(prev_btn)
        tracker_controls.addWidget(next_btn)
        tracker_controls.addStretch()
        
        tracker_layout.addWidget(self.progress_tracker)
        tracker_layout.addLayout(tracker_controls)
        
        # Notification Demo
        notification_group = QGroupBox("通知系统 (Notifications)")
        notification_layout = QVBoxLayout(notification_group)
        
        self.notification_manager = FluentNotificationManager()
        
        notification_controls = QHBoxLayout()
        info_btn = QPushButton("信息通知")
        success_btn = QPushButton("成功通知")
        warning_btn = QPushButton("警告通知")
        error_btn = QPushButton("错误通知")
        
        info_btn.clicked.connect(lambda: self.show_notification("info"))
        success_btn.clicked.connect(lambda: self.show_notification("success"))
        warning_btn.clicked.connect(lambda: self.show_notification("warning"))
        error_btn.clicked.connect(lambda: self.show_notification("error"))
        
        notification_controls.addWidget(info_btn)
        notification_controls.addWidget(success_btn)
        notification_controls.addWidget(warning_btn)
        notification_controls.addWidget(error_btn)
        
        notification_layout.addLayout(notification_controls)
        
        # Badge Demo
        badge_group = QGroupBox("徽章 (Badges)")
        badge_layout = QVBoxLayout(badge_group)
        
        badges_layout = QHBoxLayout()
        
        count_badge = FluentBadge()
        count_badge.setLabel("消息")
        count_badge.setBadgeCount(5)
        
        status_badge = FluentBadge()
        status_badge.setLabel("状态")
        status_badge.setBadgeType("active")
        
        dot_badge = FluentBadge()
        dot_badge.setLabel("提醒")
        dot_badge.setDotVisible(True)
        
        badges_layout.addWidget(count_badge)
        badges_layout.addWidget(status_badge)
        badges_layout.addWidget(dot_badge)
        badges_layout.addStretch()
        
        badge_layout.addLayout(badges_layout)
        
        # Add all groups
        self.content_layout.addWidget(status_group)
        self.content_layout.addWidget(tracker_group)
        self.content_layout.addWidget(notification_group)
        self.content_layout.addWidget(badge_group)
        self.content_layout.addStretch()
    
    def prev_step(self):
        current = self.progress_tracker.getCurrentStepIndex()
        if current > 0:
            self.progress_tracker.setCurrentStepIndex(current - 1)
    
    def next_step(self):
        current = self.progress_tracker.getCurrentStepIndex()
        max_steps = len(self.progress_tracker.getStepLabels()) - 1
        if current < max_steps:
            self.progress_tracker.setCurrentStepIndex(current + 1)
    
    def show_notification(self, type_name):
        messages = {
            "info": "这是一个信息通知",
            "success": "操作已成功完成！",
            "warning": "请注意这个警告信息",
            "error": "发生了一个错误"
        }
        
        title = f"{type_name.title()} 通知"
        message = messages[type_name]
        notification = FluentNotification(title, message, type_name)
        notification.setAutoHideEnabled(True)
        notification.setAutoHideDuration(3000)
        
        self.notification_manager.showNotification(notification)


class ComprehensiveDemoWindow(QMainWindow):
    """Main demo window showcasing all Fluent UI components"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Fluent UI 组件综合演示")
        self.setMinimumSize(1200, 800)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("Fluent UI 企业级组件库演示")
        header_font = QFont()
        header_font.setPointSize(20)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("margin: 20px; color: #0078d4;")
        
        layout.addWidget(header)
        
        # Main tab widget
        self.tab_widget = QTabWidget()
        # Add demo tabs
        self.tab_widget.addTab(DataVisualizationDemo(), "数据可视化")
        self.tab_widget.addTab(DataEntryDemo(), "数据输入")
        self.tab_widget.addTab(StatusNotificationDemo(), "状态通知")
        
        # Import and add additional demo tabs
        try:
            from examples.demo_tabs import (
                TreeHierarchyDemo, LayoutContainerDemo,
                MediaContentDemo, CommandInterfaceDemo
            )
            self.tab_widget.addTab(TreeHierarchyDemo(), "树形结构")
            self.tab_widget.addTab(LayoutContainerDemo(), "布局容器")
            self.tab_widget.addTab(MediaContentDemo(), "媒体内容")
            self.tab_widget.addTab(CommandInterfaceDemo(), "命令界面")
        except ImportError as e:
            print(f"Warning: Could not import additional demo tabs: {e}")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Fluent UI 组件库演示已就绪")
        
        # Apply theme
        self.apply_theme()
    
    def apply_theme(self):
        """Apply the Fluent theme to the entire application"""
        style = """
        QMainWindow {
            background-color: #f3f2f1;
        }
        QTabWidget::pane {
            border: 1px solid #d1d1d1;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #f3f2f1;
            border: 1px solid #d1d1d1;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #0078d4;
        }
        QTabBar::tab:hover {
            background-color: #e1dfdd;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #d1d1d1;
            border-radius: 4px;
            margin: 8px 0px;
            padding-top: 8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #323130;
        }
        """
        self.setStyleSheet(style)


def main():
    """Main entry point for the comprehensive demo"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent UI Components Demo")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Fluent UI Components")
    
    # Create and show main window
    window = ComprehensiveDemoWindow()
    window.show()
    
    # Start the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
