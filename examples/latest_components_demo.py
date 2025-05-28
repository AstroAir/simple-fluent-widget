#!/usr/bin/env python3
"""
Latest Components Demo Application

This demo showcases the latest Fluent UI components including:
- Switch Components (FluentSwitch, FluentSwitchGroup)
- Loading Components (FluentSpinner, FluentDotLoader, FluentProgressRing, FluentLoadingOverlay, FluentPulseLoader)
- Alert Components (FluentAlert, FluentNotification, FluentMessageBar)
- Pagination Components (FluentPagination, FluentSimplePagination)
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QScrollArea, QTabWidget, QWidget, QGroupBox,
    QLabel, QPushButton, QTextEdit, QSpacerItem, QSizePolicy, QSpinBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the latest components
from components.basic.switch import FluentSwitch, FluentSwitchGroup
from components.basic.loading import (
    FluentSpinner, FluentDotLoader, FluentProgressRing, 
    FluentLoadingOverlay, FluentPulseLoader
)
from components.basic.alert import (
    FluentAlert, FluentNotification, FluentMessageBar, AlertType
)
from components.basic.pagination import FluentPagination, FluentSimplePagination, PaginationMode

# Import theme
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


class SwitchDemo(ComponentDemoTab):
    """Demo for switch components"""
    
    def __init__(self):
        super().__init__(
            "开关组件 (Switch)",
            "现代化的开关控件，支持多种尺寸、平滑动画、标签文本和键盘导航"
        )
    
    def setup_content(self):
        # Basic switches
        basic_group = QGroupBox("基础开关")
        basic_layout = QVBoxLayout(basic_group)
        
        # Different sizes
        sizes_layout = QHBoxLayout()
        
        small_switch = FluentSwitch()
        small_switch.setSize(FluentSwitch.SIZE_SMALL)
        small_switch.setText("Small")
        sizes_layout.addWidget(QLabel("小号:"))
        sizes_layout.addWidget(small_switch)
        
        medium_switch = FluentSwitch()
        medium_switch.setSize(FluentSwitch.SIZE_MEDIUM)
        medium_switch.setText("Medium")
        medium_switch.setChecked(True)
        sizes_layout.addWidget(QLabel("中号:"))
        sizes_layout.addWidget(medium_switch)
        
        large_switch = FluentSwitch()
        large_switch.setSize(FluentSwitch.SIZE_LARGE)
        large_switch.setText("Large")
        sizes_layout.addWidget(QLabel("大号:"))
        sizes_layout.addWidget(large_switch)
        
        sizes_layout.addStretch()
        basic_layout.addLayout(sizes_layout)
        
        # Switches with custom text
        text_layout = QHBoxLayout()
        
        on_off_switch = FluentSwitch()
        on_off_switch.setOnText("开启")
        on_off_switch.setOffText("关闭")
        text_layout.addWidget(QLabel("自定义文本:"))
        text_layout.addWidget(on_off_switch)
        
        yes_no_switch = FluentSwitch()
        yes_no_switch.setOnText("是")
        yes_no_switch.setOffText("否")
        yes_no_switch.setChecked(True)
        text_layout.addWidget(QLabel("是/否:"))
        text_layout.addWidget(yes_no_switch)
        
        text_layout.addStretch()
        basic_layout.addLayout(text_layout)
        
        # Disabled switch
        disabled_layout = QHBoxLayout()
        disabled_switch = FluentSwitch()
        disabled_switch.setText("Disabled")
        disabled_switch.setChecked(True)
        disabled_switch.setEnabled(False)
        disabled_layout.addWidget(QLabel("禁用状态:"))
        disabled_layout.addWidget(disabled_switch)
        disabled_layout.addStretch()
        basic_layout.addLayout(disabled_layout)
        
        self.content_layout.addWidget(basic_group)
        
        # Switch group
        group_widget = QGroupBox("开关组")
        group_layout = QVBoxLayout(group_widget)
        
        self.switch_group = FluentSwitchGroup()
        
        # Add switches to group
        notification_switch = FluentSwitch()
        notification_switch.setText("推送通知")
        notification_switch.setChecked(True)
        self.switch_group.addSwitch("notifications", notification_switch)
        
        email_switch = FluentSwitch()
        email_switch.setText("邮件提醒")
        self.switch_group.addSwitch("email", email_switch)
        
        sound_switch = FluentSwitch()
        sound_switch.setText("声音提醒")
        sound_switch.setChecked(True)
        self.switch_group.addSwitch("sound", sound_switch)
        
        dark_mode_switch = FluentSwitch()
        dark_mode_switch.setText("深色模式")
        self.switch_group.addSwitch("dark_mode", dark_mode_switch)
        
        group_layout.addWidget(self.switch_group)
        
        # Status display
        self.status_label = QLabel("当前状态: 无")
        group_layout.addWidget(self.status_label)
        
        # Connect signal
        self.switch_group.switchToggled.connect(self.on_switch_toggled)
        
        self.content_layout.addWidget(group_widget)
    
    def on_switch_toggled(self, switch_id: str, checked: bool):
        """Handle switch toggle"""
        status = "开启" if checked else "关闭"
        self.status_label.setText(f"当前状态: {switch_id} - {status}")


class LoadingDemo(ComponentDemoTab):
    """Demo for loading components"""
    
    def __init__(self):
        super().__init__(
            "加载组件 (Loading)",
            "多种加载指示器，包括旋转器、点阵加载器、进度环、覆盖层和脉冲加载器"
        )
    
    def setup_content(self):
        # Basic loading indicators
        basic_group = QGroupBox("基础加载指示器")
        basic_layout = QHBoxLayout(basic_group)
        
        # Spinner
        spinner_layout = QVBoxLayout()
        spinner_layout.addWidget(QLabel("旋转器"))
        self.spinner = FluentSpinner()
        self.spinner.setFixedSize(40, 40)
        spinner_layout.addWidget(self.spinner)
        basic_layout.addLayout(spinner_layout)
        
        # Dot Loader
        dots_layout = QVBoxLayout()
        dots_layout.addWidget(QLabel("点阵加载器"))
        self.dot_loader = FluentDotLoader()
        self.dot_loader.setFixedHeight(40)
        dots_layout.addWidget(self.dot_loader)
        basic_layout.addLayout(dots_layout)
        
        # Progress Ring
        ring_layout = QVBoxLayout()
        ring_layout.addWidget(QLabel("进度环"))
        self.progress_ring = FluentProgressRing()
        self.progress_ring.setFixedSize(60, 60)
        self.progress_ring.setValue(60)
        ring_layout.addWidget(self.progress_ring)
        basic_layout.addLayout(ring_layout)
        
        # Pulse Loader
        pulse_layout = QVBoxLayout()
        pulse_layout.addWidget(QLabel("脉冲加载器"))
        self.pulse_loader = FluentPulseLoader()
        self.pulse_loader.setFixedSize(40, 40)
        pulse_layout.addWidget(self.pulse_loader)
        basic_layout.addLayout(pulse_layout)
        
        basic_layout.addStretch()
        self.content_layout.addWidget(basic_group)
        
        # Controls
        controls_group = QGroupBox("控制面板")
        controls_layout = QHBoxLayout(controls_group)
        
        # Start/Stop button
        self.toggle_btn = QPushButton("停止加载")
        self.toggle_btn.clicked.connect(self.toggle_loading)
        controls_layout.addWidget(self.toggle_btn)
        
        # Progress control
        controls_layout.addWidget(QLabel("进度:"))
        self.progress_spin = QSpinBox()
        self.progress_spin.setRange(0, 100)
        self.progress_spin.setValue(60)
        self.progress_spin.valueChanged.connect(self.update_progress)
        controls_layout.addWidget(self.progress_spin)
        
        # Show overlay button
        self.overlay_btn = QPushButton("显示覆盖层")
        self.overlay_btn.clicked.connect(self.show_overlay)
        controls_layout.addWidget(self.overlay_btn)
        
        controls_layout.addStretch()
        self.content_layout.addWidget(controls_group)
        
        # Start animations
        self.start_loading()
    
    def toggle_loading(self):
        """Toggle loading animations"""
        if self.spinner.isRunning():
            self.stop_loading()
            self.toggle_btn.setText("开始加载")
        else:
            self.start_loading()
            self.toggle_btn.setText("停止加载")
    
    def start_loading(self):
        """Start all loading animations"""
        self.spinner.start()
        self.dot_loader.start()
        self.pulse_loader.start()
    
    def stop_loading(self):
        """Stop all loading animations"""
        self.spinner.stop()
        self.dot_loader.stop()
        self.pulse_loader.stop()
    
    def update_progress(self, value):
        """Update progress ring value"""
        self.progress_ring.setValue(value)
    
    def show_overlay(self):
        """Show loading overlay"""
        self.overlay = FluentLoadingOverlay(self)
        self.overlay.show("加载中，请稍候...")
        
        # Auto hide after 3 seconds
        QTimer.singleShot(3000, self.overlay.hide)


class AlertDemo(ComponentDemoTab):
    """Demo for alert components"""
    
    def __init__(self):
        super().__init__(
            "提醒组件 (Alert)",
            "多种提醒组件，包括内联提醒、浮动通知和消息条，支持多种严重性级别"
        )
    
    def setup_content(self):
        # Inline alerts
        alerts_group = QGroupBox("内联提醒")
        alerts_layout = QVBoxLayout(alerts_group)
        
        # Different alert types
        info_alert = FluentAlert(AlertType.INFO, "这是一条信息提醒")
        info_alert.setDismissible(True)
        alerts_layout.addWidget(info_alert)
        
        success_alert = FluentAlert(AlertType.SUCCESS, "操作成功完成！")
        success_alert.setDismissible(True)
        alerts_layout.addWidget(success_alert)
        
        warning_alert = FluentAlert(AlertType.WARNING, "请注意：此操作需要谨慎处理")
        warning_alert.setDismissible(True)
        alerts_layout.addWidget(warning_alert)
        
        error_alert = FluentAlert(AlertType.ERROR, "发生错误：无法完成操作")
        error_alert.setDismissible(True)
        alerts_layout.addWidget(error_alert)
        
        self.content_layout.addWidget(alerts_group)
        
        # Message bars
        bars_group = QGroupBox("消息条")
        bars_layout = QVBoxLayout(bars_group)
        
        info_bar = FluentMessageBar(AlertType.INFO, "系统更新", "新版本已可用，建议立即更新")
        info_bar.setDismissible(True)
        bars_layout.addWidget(info_bar)
        
        success_bar = FluentMessageBar(AlertType.SUCCESS, "备份完成", "数据已成功备份到云端")
        success_bar.setDismissible(True)
        bars_layout.addWidget(success_bar)
        
        self.content_layout.addWidget(bars_group)
        
        # Control buttons
        controls_group = QGroupBox("通知控制")
        controls_layout = QHBoxLayout(controls_group)
        
        # Notification buttons
        info_btn = QPushButton("信息通知")
        info_btn.clicked.connect(lambda: self.show_notification(AlertType.INFO, "信息", "这是一条信息通知"))
        controls_layout.addWidget(info_btn)
        
        success_btn = QPushButton("成功通知")
        success_btn.clicked.connect(lambda: self.show_notification(AlertType.SUCCESS, "成功", "操作已成功完成"))
        controls_layout.addWidget(success_btn)
        
        warning_btn = QPushButton("警告通知")
        warning_btn.clicked.connect(lambda: self.show_notification(AlertType.WARNING, "警告", "请检查您的设置"))
        controls_layout.addWidget(warning_btn)
        
        error_btn = QPushButton("错误通知")
        error_btn.clicked.connect(lambda: self.show_notification(AlertType.ERROR, "错误", "发生了未知错误"))
        controls_layout.addWidget(error_btn)
        
        controls_layout.addStretch()
        self.content_layout.addWidget(controls_group)
    
    def show_notification(self, alert_type: AlertType, title: str, message: str):
        """Show a notification"""
        notification = FluentNotification(alert_type, title, message, self)
        notification.setAutoHide(True)
        notification.setDuration(4000)
        notification.show()


class PaginationDemo(ComponentDemoTab):
    """Demo for pagination components"""
    
    def __init__(self):
        super().__init__(
            "分页组件 (Pagination)",
            "完整的分页控件，支持多种显示模式、页面大小选择和跳转功能"
        )
    
    def setup_content(self):
        # Full pagination
        full_group = QGroupBox("完整分页")
        full_layout = QVBoxLayout(full_group)
        
        self.full_pagination = FluentPagination()
        self.full_pagination.setMode(PaginationMode.FULL)
        self.full_pagination.setTotalItems(1000)
        self.full_pagination.setPageSize(20)
        self.full_pagination.setCurrentPage(5)
        self.full_pagination.setShowPageSizeSelector(True)
        self.full_pagination.setShowQuickJump(True)
        full_layout.addWidget(self.full_pagination)
        
        # Status label for full pagination
        self.full_status = QLabel()
        self.update_full_status()
        full_layout.addWidget(self.full_status)
        
        self.content_layout.addWidget(full_group)
        
        # Simple pagination
        simple_group = QGroupBox("简单分页")
        simple_layout = QVBoxLayout(simple_group)
        
        self.simple_pagination = FluentSimplePagination()
        self.simple_pagination.setTotalItems(500)
        self.simple_pagination.setPageSize(25)
        self.simple_pagination.setCurrentPage(3)
        simple_layout.addWidget(self.simple_pagination)
        
        # Status label for simple pagination
        self.simple_status = QLabel()
        self.update_simple_status()
        simple_layout.addWidget(self.simple_status)
        
        self.content_layout.addWidget(simple_group)
        
        # Compact pagination
        compact_group = QGroupBox("紧凑分页")
        compact_layout = QVBoxLayout(compact_group)
        
        self.compact_pagination = FluentPagination()
        self.compact_pagination.setMode(PaginationMode.COMPACT)
        self.compact_pagination.setTotalItems(100)
        self.compact_pagination.setPageSize(10)
        self.compact_pagination.setCurrentPage(2)
        compact_layout.addWidget(self.compact_pagination)
        
        # Status label for compact pagination
        self.compact_status = QLabel()
        self.update_compact_status()
        compact_layout.addWidget(self.compact_status)
        
        self.content_layout.addWidget(compact_group)
        
        # Connect signals
        self.full_pagination.pageChanged.connect(self.on_full_page_changed)
        self.full_pagination.pageSizeChanged.connect(self.on_full_page_size_changed)
        self.simple_pagination.pageChanged.connect(self.on_simple_page_changed)
        self.compact_pagination.pageChanged.connect(self.on_compact_page_changed)
    
    def update_full_status(self):
        """Update full pagination status"""
        page = self.full_pagination.currentPage()
        size = self.full_pagination.pageSize()
        total = self.full_pagination.totalItems()
        total_pages = self.full_pagination.totalPages()
        start = (page - 1) * size + 1
        end = min(page * size, total)
        self.full_status.setText(f"显示 {start}-{end} 条，共 {total} 条记录，第 {page}/{total_pages} 页")
    
    def update_simple_status(self):
        """Update simple pagination status"""
        page = self.simple_pagination.currentPage()
        size = self.simple_pagination.pageSize()
        total = self.simple_pagination.totalItems()
        total_pages = self.simple_pagination.totalPages()
        start = (page - 1) * size + 1
        end = min(page * size, total)
        self.simple_status.setText(f"显示 {start}-{end} 条，共 {total} 条记录，第 {page}/{total_pages} 页")
    
    def update_compact_status(self):
        """Update compact pagination status"""
        page = self.compact_pagination.currentPage()
        size = self.compact_pagination.pageSize()
        total = self.compact_pagination.totalItems()
        total_pages = self.compact_pagination.totalPages()
        start = (page - 1) * size + 1
        end = min(page * size, total)
        self.compact_status.setText(f"显示 {start}-{end} 条，共 {total} 条记录，第 {page}/{total_pages} 页")
    
    def on_full_page_changed(self, page):
        """Handle full pagination page change"""
        self.update_full_status()
    
    def on_full_page_size_changed(self, size):
        """Handle full pagination page size change"""
        self.update_full_status()
    
    def on_simple_page_changed(self, page):
        """Handle simple pagination page change"""
        self.update_simple_status()
    
    def on_compact_page_changed(self, page):
        """Handle compact pagination page change"""
        self.update_compact_status()


class LatestComponentsDemo(QMainWindow):
    """Main demo window for latest components"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("最新组件演示 - Latest Components Demo")
        self.setMinimumSize(1000, 700)
        self.setup_ui()
        self.apply_theme()
        
        # Connect theme change signal
        theme_manager.theme_changed.connect(self.apply_theme)
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 10)
        
        title_label = QLabel("Fluent UI 最新组件演示")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Theme toggle button
        self.theme_btn = QPushButton("切换主题")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)
        
        layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        tabs = [
            ("开关组件", SwitchDemo()),
            ("加载组件", LoadingDemo()),
            ("提醒组件", AlertDemo()),
            ("分页组件", PaginationDemo())
        ]
        
        for tab_name, tab_widget in tabs:
            # Create scroll area for each tab
            scroll_area = QScrollArea()
            scroll_area.setWidget(tab_widget)
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            self.tab_widget.addTab(scroll_area, tab_name)
        
        layout.addWidget(self.tab_widget)
    
    def apply_theme(self):
        """Apply current theme"""
        bg_color = theme_manager.get_color('background')
        text_color = theme_manager.get_color('on_background')
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme_manager.get_color('outline')};
                background-color: {bg_color};
            }}
            QTabBar::tab {{
                background-color: {theme_manager.get_color('surface')};
                color: {text_color};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('on_primary')};
            }}
            QScrollArea {{
                border: none;
                background-color: {bg_color};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme_manager.get_color('outline')};
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: {theme_manager.get_color('surface')};
                color: {text_color};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {theme_manager.get_color('primary')};
            }}
            QLabel {{
                color: {text_color};
            }}
            QPushButton {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('on_primary')};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('primary_hover')};
            }}
            QPushButton:pressed {{
                background-color: {theme_manager.get_color('primary_pressed')};
            }}
        """)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if theme_manager.is_dark_mode():
            theme_manager.set_light_mode()
        else:
            theme_manager.set_dark_mode()


def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Create and show demo window
    demo = LatestComponentsDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
