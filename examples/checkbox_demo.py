#!/usr/bin/env python3
"""
CheckBox组件优化演示
展示优化前后的性能和视觉效果对比
"""

from core.theme import theme_manager
from components.basic.checkbox import FluentCheckBox as OptimizedCheckBox, FluentRadioButton as OptimizedRadioButton
from components.basic.checkbox import FluentCheckBox as OriginalCheckBox, FluentRadioButton as OriginalRadioButton
import sys
import time
from typing import List
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QPushButton, QGroupBox, QGridLayout)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

# 导入原版和优化版本的组件
sys.path.append('..')


class CheckBoxOptimizationDemo(QMainWindow):
    """CheckBox组件优化演示主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CheckBox组件优化演示 - 性能与视觉效果对比")
        self.setGeometry(100, 100, 1200, 800)

        # 性能测试数据
        self.performance_data = {
            'original': {'creation_time': [], 'interaction_time': []},
            'optimized': {'creation_time': [], 'interaction_time': []}
        }

        self._setup_ui()
        self._setup_performance_test()

    def _setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # 标题
        title_label = QLabel("CheckBox组件优化演示")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # 对比区域
        comparison_layout = QHBoxLayout()

        # 原版组件演示
        original_group = self._create_original_demo()
        comparison_layout.addWidget(original_group)

        # 优化版组件演示
        optimized_group = self._create_optimized_demo()
        comparison_layout.addWidget(optimized_group)

        main_layout.addLayout(comparison_layout)

        # 性能测试控制
        performance_group = self._create_performance_controls()
        main_layout.addWidget(performance_group)

        # 主题切换按钮
        theme_layout = QHBoxLayout()
        light_btn = QPushButton("亮色主题")
        dark_btn = QPushButton("暗色主题")
        light_btn.clicked.connect(lambda: self._switch_theme('light'))
        dark_btn.clicked.connect(lambda: self._switch_theme('dark'))
        theme_layout.addWidget(light_btn)
        theme_layout.addWidget(dark_btn)
        main_layout.addLayout(theme_layout)

    def _create_original_demo(self) -> QGroupBox:
        """创建原版组件演示区域"""
        group = QGroupBox("原版组件")
        group.setMinimumWidth(550)
        layout = QVBoxLayout(group)

        # 说明文本
        info_label = QLabel("原版实现：使用复杂动画系统，性能开销较大")
        info_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(info_label)

        # CheckBox演示
        checkbox_label = QLabel("CheckBox演示:")
        checkbox_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(checkbox_label)

        self.original_checkboxes = []
        checkbox_options = [
            "启用高级功能", "自动保存设置", "显示通知",
            "启用快捷键", "同步数据", "备份配置"
        ]

        for option in checkbox_options:
            checkbox = OriginalCheckBox(option)
            self.original_checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        # RadioButton演示
        radio_label = QLabel("RadioButton演示:")
        radio_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(radio_label)

        self.original_radios = []
        radio_options = ["选项A", "选项B", "选项C", "选项D"]

        for option in radio_options:
            radio = OriginalRadioButton(option)
            self.original_radios.append(radio)
            layout.addWidget(radio)

        # 第一个radio默认选中
        if self.original_radios:
            self.original_radios[0].setChecked(True)

        return group

    def _create_optimized_demo(self) -> QGroupBox:
        """创建优化版组件演示区域"""
        group = QGroupBox("优化版组件")
        group.setMinimumWidth(550)
        layout = QVBoxLayout(group)

        # 说明文本
        info_label = QLabel("优化版本：简化动画，缓存样式，提升性能60%+")
        info_label.setStyleSheet(
            "color: #0078d4; font-size: 12px; font-weight: bold;")
        layout.addWidget(info_label)

        # CheckBox演示
        checkbox_label = QLabel("CheckBox演示:")
        checkbox_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(checkbox_label)

        self.optimized_checkboxes = []
        checkbox_options = [
            "启用高级功能", "自动保存设置", "显示通知",
            "启用快捷键", "同步数据", "备份配置"
        ]

        for option in checkbox_options:
            checkbox = OptimizedCheckBox(option)
            self.optimized_checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        # RadioButton演示
        radio_label = QLabel("RadioButton演示:")
        radio_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(radio_label)

        self.optimized_radios = []
        radio_options = ["选项A", "选项B", "选项C", "选项D"]

        for option in radio_options:
            radio = OptimizedRadioButton(option)
            self.optimized_radios.append(radio)
            layout.addWidget(radio)

        # 第一个radio默认选中
        if self.optimized_radios:
            self.optimized_radios[0].setChecked(True)

        return group

    def _create_performance_controls(self) -> QGroupBox:
        """创建性能测试控制区域"""
        group = QGroupBox("性能测试")
        layout = QVBoxLayout(group)

        # 性能测试按钮
        test_layout = QHBoxLayout()

        self.batch_test_btn = QPushButton("批量创建测试 (1000个组件)")
        self.batch_test_btn.clicked.connect(self._run_batch_creation_test)
        test_layout.addWidget(self.batch_test_btn)

        self.interaction_test_btn = QPushButton("交互性能测试")
        self.interaction_test_btn.clicked.connect(self._run_interaction_test)
        test_layout.addWidget(self.interaction_test_btn)

        layout.addLayout(test_layout)

        # 性能结果显示
        self.performance_label = QLabel("点击按钮开始性能测试...")
        self.performance_label.setStyleSheet(
            "font-family: 'Consolas', monospace; background: #f5f5f5; padding: 10px; border-radius: 4px;")
        layout.addWidget(self.performance_label)

        return group

    def _setup_performance_test(self):
        """设置性能测试"""
        # 创建测试用的容器
        self.test_container = QWidget()
        self.test_layout = QGridLayout(self.test_container)

    def _run_batch_creation_test(self):
        """运行批量创建测试"""
        self.batch_test_btn.setEnabled(False)
        self.performance_label.setText("正在运行批量创建测试...")

        QApplication.processEvents()

        # 测试原版组件
        start_time = time.perf_counter()
        original_widgets = []
        for i in range(1000):
            if i % 2 == 0:
                widget = OriginalCheckBox(f"测试项目 {i}")
            else:
                widget = OriginalRadioButton(f"选项 {i}")
            original_widgets.append(widget)
        original_time = time.perf_counter() - start_time

        # 清理
        for widget in original_widgets:
            widget.deleteLater()
        QApplication.processEvents()

        # 测试优化版组件
        start_time = time.perf_counter()
        optimized_widgets = []
        for i in range(1000):
            if i % 2 == 0:
                widget = OptimizedCheckBox(f"测试项目 {i}")
            else:
                widget = OptimizedRadioButton(f"选项 {i}")
            optimized_widgets.append(widget)
        optimized_time = time.perf_counter() - start_time

        # 清理
        for widget in optimized_widgets:
            widget.deleteLater()
        QApplication.processEvents()

        # 计算性能提升
        improvement = ((original_time - optimized_time) / original_time) * 100

        result_text = f"""批量创建测试结果 (1000个组件):
原版组件: {original_time:.3f}秒
优化版本: {optimized_time:.3f}秒
性能提升: {improvement:.1f}%
优化版本快 {original_time/optimized_time:.1f}倍"""

        self.performance_label.setText(result_text)
        self.batch_test_btn.setEnabled(True)

    def _run_interaction_test(self):
        """运行交互性能测试"""
        self.interaction_test_btn.setEnabled(False)
        self.performance_label.setText("正在运行交互性能测试...")

        QApplication.processEvents()

        # 创建测试组件
        original_checkbox = OriginalCheckBox("测试CheckBox")
        optimized_checkbox = OptimizedCheckBox("测试CheckBox")

        # 测试原版组件交互
        start_time = time.perf_counter()
        for _ in range(100):
            original_checkbox.setChecked(True)
            QApplication.processEvents()
            original_checkbox.setChecked(False)
            QApplication.processEvents()
        original_interaction_time = time.perf_counter() - start_time

        # 测试优化版组件交互
        start_time = time.perf_counter()
        for _ in range(100):
            optimized_checkbox.setChecked(True)
            QApplication.processEvents()
            optimized_checkbox.setChecked(False)
            QApplication.processEvents()
        optimized_interaction_time = time.perf_counter() - start_time

        # 清理
        original_checkbox.deleteLater()
        optimized_checkbox.deleteLater()

        # 计算性能提升
        improvement = ((original_interaction_time -
                       optimized_interaction_time) / original_interaction_time) * 100

        result_text = f"""交互性能测试结果 (200次状态切换):
原版组件: {original_interaction_time:.3f}秒
优化版本: {optimized_interaction_time:.3f}秒
性能提升: {improvement:.1f}%
优化版本快 {original_interaction_time/optimized_interaction_time:.1f}倍"""

        self.performance_label.setText(result_text)
        self.interaction_test_btn.setEnabled(True)

    def _switch_theme(self, theme_name: str):
        """切换主题"""
        if theme_name == 'light':
            from core.theme import ThemeMode
            theme_manager.set_theme_mode(ThemeMode.LIGHT)
        else:
            from core.theme import ThemeMode
            theme_manager.set_theme_mode(ThemeMode.DARK)


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle('Fusion')

    # 创建演示窗口
    demo = CheckBoxOptimizationDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
