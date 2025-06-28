"""
FluentSpinBox 组件详细使用示例界面
展示所有功能和交互效果
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QLabel, QSlider, QCheckBox, QPushButton,
    QScrollArea, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from components.basic.spinbox import FluentSpinBox, FluentDoubleSpinBox, FluentNumberInput
from core.theme import theme_manager, ThemeMode


class SpinBoxDemoWindow(QMainWindow):
    """FluentSpinBox 组件演示窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FluentSpinBox 组件使用示例")
        self.setGeometry(100, 100, 1200, 800)

        # 存储所有组件引用
        self.components = {}
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self._update_demo_values)

        self._setup_ui()
        self._connect_signals()

        # 应用初始主题
        theme_manager.set_theme_mode(ThemeMode.LIGHT)

    def _setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("FluentSpinBox 组件演示")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        main_layout.addWidget(title_label)

        # 控制面板
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # 基础组件示例
        basic_group = self._create_basic_examples()
        scroll_layout.addWidget(basic_group)

        # 高级功能示例
        advanced_group = self._create_advanced_examples()
        scroll_layout.addWidget(advanced_group)

        # 交互演示
        interaction_group = self._create_interaction_examples()
        scroll_layout.addWidget(interaction_group)

        # 样式变体示例
        style_group = self._create_style_examples()
        scroll_layout.addWidget(style_group)

        # 实际应用场景
        application_group = self._create_application_examples()
        scroll_layout.addWidget(application_group)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

    def _create_control_panel(self) -> QGroupBox:
        """创建控制面板"""
        group = QGroupBox("控制面板")
        layout = QHBoxLayout(group)

        # 主题切换
        theme_label = QLabel("主题:")
        self.theme_checkbox = QCheckBox("深色模式")
        self.theme_checkbox.stateChanged.connect(self._on_theme_changed)

        # 动画演示
        self.demo_button = QPushButton("开始动画演示")
        self.demo_button.clicked.connect(self._toggle_demo)

        # 重置按钮
        reset_button = QPushButton("重置所有值")
        reset_button.clicked.connect(self._reset_all_values)

        layout.addWidget(theme_label)
        layout.addWidget(self.theme_checkbox)
        layout.addStretch()
        layout.addWidget(self.demo_button)
        layout.addWidget(reset_button)

        return group

    def _create_basic_examples(self) -> QGroupBox:
        """创建基础示例"""
        group = QGroupBox("基础 SpinBox 组件")
        layout = QGridLayout(group)

        # 1. 基础整数输入
        layout.addWidget(QLabel("基础整数输入:"), 0, 0)
        basic_int = FluentSpinBox()
        basic_int.setRange(0, 100)
        basic_int.setValue(50)
        basic_int.setToolTip("基础整数输入框，范围 0-100")
        self.components['basic_int'] = basic_int
        layout.addWidget(basic_int, 0, 1)

        value_label1 = QLabel("值: 50")
        basic_int.valueChanged.connect(
            lambda v: value_label1.setText(f"值: {v}"))
        layout.addWidget(value_label1, 0, 2)

        # 2. 基础浮点数输入
        layout.addWidget(QLabel("基础浮点数输入:"), 1, 0)
        basic_double = FluentDoubleSpinBox()
        basic_double.setRange(0.0, 10.0)
        basic_double.setValue(5.0)
        basic_double.setDecimals(2)
        basic_double.setSingleStep(0.1)
        basic_double.setToolTip("基础浮点数输入框，范围 0.0-10.0")
        self.components['basic_double'] = basic_double
        layout.addWidget(basic_double, 1, 1)

        value_label2 = QLabel("值: 5.00")
        basic_double.valueChanged.connect(
            lambda v: value_label2.setText(f"值: {v:.2f}"))
        layout.addWidget(value_label2, 1, 2)

        # 3. 负数范围
        layout.addWidget(QLabel("负数范围:"), 2, 0)
        negative_spin = FluentSpinBox()
        negative_spin.setRange(-100, 100)
        negative_spin.setValue(0)
        negative_spin.setToolTip("支持负数的输入框，范围 -100 到 100")
        self.components['negative'] = negative_spin
        layout.addWidget(negative_spin, 2, 1)

        value_label3 = QLabel("值: 0")
        negative_spin.valueChanged.connect(
            lambda v: value_label3.setText(f"值: {v}"))
        layout.addWidget(value_label3, 2, 2)

        # 4. 大数值范围
        layout.addWidget(QLabel("大数值范围:"), 3, 0)
        large_spin = FluentSpinBox()
        large_spin.setRange(1000, 999999)
        large_spin.setValue(50000)
        large_spin.setSingleStep(1000)
        large_spin.setToolTip("大数值范围输入框")
        self.components['large'] = large_spin
        layout.addWidget(large_spin, 3, 1)

        value_label4 = QLabel("值: 50000")
        large_spin.valueChanged.connect(
            lambda v: value_label4.setText(f"值: {v:,}"))
        layout.addWidget(value_label4, 3, 2)

        return group

    def _create_advanced_examples(self) -> QGroupBox:
        """创建高级功能示例"""
        group = QGroupBox("高级功能演示")
        layout = QGridLayout(group)

        # 1. 动画值设置
        layout.addWidget(QLabel("动画值设置:"), 0, 0)
        animated_spin = FluentSpinBox()
        animated_spin.setRange(0, 100)
        self.components['animated'] = animated_spin
        layout.addWidget(animated_spin, 0, 1)

        # 动画控制按钮
        anim_layout = QHBoxLayout()
        btn_25 = QPushButton("25")
        btn_25.clicked.connect(lambda: animated_spin.set_value_animated(25))
        btn_50 = QPushButton("50")
        btn_50.clicked.connect(lambda: animated_spin.set_value_animated(50))
        btn_75 = QPushButton("75")
        btn_75.clicked.connect(lambda: animated_spin.set_value_animated(75))
        btn_100 = QPushButton("100")
        btn_100.clicked.connect(lambda: animated_spin.set_value_animated(100))

        anim_layout.addWidget(btn_25)
        anim_layout.addWidget(btn_50)
        anim_layout.addWidget(btn_75)
        anim_layout.addWidget(btn_100)
        layout.addLayout(anim_layout, 0, 2)

        # 2. 精度控制
        layout.addWidget(QLabel("精度控制:"), 1, 0)
        precision_spin = FluentDoubleSpinBox()
        precision_spin.setRange(0.0, 1.0)
        precision_spin.setValue(0.5)
        precision_spin.setDecimals(4)
        precision_spin.setSingleStep(0.0001)
        self.components['precision'] = precision_spin
        layout.addWidget(precision_spin, 1, 1)

        precision_label = QLabel("高精度: 0.5000")
        precision_spin.valueChanged.connect(
            lambda v: precision_label.setText(f"高精度: {v:.4f}")
        )
        layout.addWidget(precision_label, 1, 2)

        # 3. 步长控制
        layout.addWidget(QLabel("可变步长:"), 2, 0)
        step_spin = FluentSpinBox()
        step_spin.setRange(0, 1000)
        step_spin.setValue(100)
        self.components['step'] = step_spin
        layout.addWidget(step_spin, 2, 1)

        # 步长控制滑块
        step_layout = QVBoxLayout()
        step_slider = QSlider(Qt.Orientation.Horizontal)
        step_slider.setRange(1, 50)
        step_slider.setValue(1)
        step_slider.valueChanged.connect(lambda v: step_spin.setSingleStep(v))
        step_layout.addWidget(QLabel("步长:"))
        step_layout.addWidget(step_slider)
        step_label = QLabel("步长: 1")
        step_slider.valueChanged.connect(
            lambda v: step_label.setText(f"步长: {v}"))
        step_layout.addWidget(step_label)
        layout.addLayout(step_layout, 2, 2)

        return group

    def _create_interaction_examples(self) -> QGroupBox:
        """创建交互演示"""
        group = QGroupBox("交互效果演示")
        layout = QGridLayout(group)

        # 1. 鼠标滚轮交互
        layout.addWidget(QLabel("鼠标滚轮:"), 0, 0)
        wheel_spin = FluentSpinBox()
        wheel_spin.setRange(0, 100)
        wheel_spin.setValue(50)
        wheel_spin.setFocus()  # 默认获得焦点以便滚轮操作
        self.components['wheel'] = wheel_spin
        layout.addWidget(wheel_spin, 0, 1)
        layout.addWidget(QLabel("(获得焦点后可用滚轮调节)"), 0, 2)

        # 2. 键盘交互
        layout.addWidget(QLabel("键盘交互:"), 1, 0)
        keyboard_spin = FluentSpinBox()
        keyboard_spin.setRange(0, 100)
        keyboard_spin.setValue(50)
        self.components['keyboard'] = keyboard_spin
        layout.addWidget(keyboard_spin, 1, 1)
        layout.addWidget(QLabel("(使用上下箭头键或PageUp/PageDown)"), 1, 2)

        # 3. 禁用状态
        layout.addWidget(QLabel("启用/禁用:"), 2, 0)
        disabled_spin = FluentSpinBox()
        disabled_spin.setRange(0, 100)
        disabled_spin.setValue(50)
        self.components['disabled'] = disabled_spin
        layout.addWidget(disabled_spin, 2, 1)

        enable_checkbox = QCheckBox("启用")
        enable_checkbox.setChecked(True)
        enable_checkbox.stateChanged.connect(
            lambda state: disabled_spin.setEnabled(
                state == Qt.CheckState.Checked)
        )
        layout.addWidget(enable_checkbox, 2, 2)

        # 4. 只读模式
        layout.addWidget(QLabel("只读模式:"), 3, 0)
        readonly_spin = FluentSpinBox()
        readonly_spin.setRange(0, 100)
        readonly_spin.setValue(75)
        readonly_spin.setReadOnly(True)
        self.components['readonly'] = readonly_spin
        layout.addWidget(readonly_spin, 3, 1)
        layout.addWidget(QLabel("(只读，不可编辑)"), 3, 2)

        return group

    def _create_style_examples(self) -> QGroupBox:
        """创建样式变体示例"""
        group = QGroupBox("FluentNumberInput 增强组件")
        layout = QGridLayout(group)

        # 1. 基础数字输入
        layout.addWidget(QLabel("基础数字输入:"), 0, 0)
        number_input1 = FluentNumberInput(
            minimum=0, maximum=100, decimals=0, step=1)
        number_input1.set_value(25)
        self.components['number1'] = number_input1
        layout.addWidget(number_input1, 0, 1)

        value_label5 = QLabel("值: 25")
        number_input1.value_changed.connect(
            lambda v: value_label5.setText(f"值: {int(v)}"))
        layout.addWidget(value_label5, 0, 2)

        # 2. 浮点数输入
        layout.addWidget(QLabel("浮点数输入:"), 1, 0)
        number_input2 = FluentNumberInput(
            minimum=0.0, maximum=10.0, decimals=2, step=0.25)
        number_input2.set_value(5.0)
        self.components['number2'] = number_input2
        layout.addWidget(number_input2, 1, 1)

        value_label6 = QLabel("值: 5.00")
        number_input2.value_changed.connect(
            lambda v: value_label6.setText(f"值: {v:.2f}"))
        layout.addWidget(value_label6, 1, 2)

        # 3. 大步长
        layout.addWidget(QLabel("大步长调节:"), 2, 0)
        number_input3 = FluentNumberInput(
            minimum=0, maximum=1000, decimals=0, step=50)
        number_input3.set_value(250)
        self.components['number3'] = number_input3
        layout.addWidget(number_input3, 2, 1)

        value_label7 = QLabel("值: 250")
        number_input3.value_changed.connect(
            lambda v: value_label7.setText(f"值: {int(v)}"))
        layout.addWidget(value_label7, 2, 2)

        # 4. 小步长精确调节
        layout.addWidget(QLabel("精确调节:"), 3, 0)
        number_input4 = FluentNumberInput(
            minimum=0.0, maximum=1.0, decimals=3, step=0.001)
        number_input4.set_value(0.5)
        self.components['number4'] = number_input4
        layout.addWidget(number_input4, 3, 1)

        value_label8 = QLabel("值: 0.500")
        number_input4.value_changed.connect(
            lambda v: value_label8.setText(f"值: {v:.3f}"))
        layout.addWidget(value_label8, 3, 2)

        return group

    def _create_application_examples(self) -> QGroupBox:
        """创建实际应用场景示例"""
        group = QGroupBox("实际应用场景")
        layout = QGridLayout(group)

        # 1. 音量控制
        layout.addWidget(QLabel("🔊 音量控制:"), 0, 0)
        volume_control = FluentNumberInput(
            minimum=0, maximum=100, decimals=0, step=5)
        volume_control.set_value(75)
        self.components['volume'] = volume_control
        layout.addWidget(volume_control, 0, 1)

        volume_label = QLabel("音量: 75%")
        volume_control.value_changed.connect(
            lambda v: volume_label.setText(f"音量: {int(v)}%"))
        layout.addWidget(volume_label, 0, 2)

        # 2. 温度设置
        layout.addWidget(QLabel("🌡️ 温度设置:"), 1, 0)
        temp_control = FluentDoubleSpinBox()
        temp_control.setRange(16.0, 30.0)
        temp_control.setValue(22.5)
        temp_control.setDecimals(1)
        temp_control.setSingleStep(0.5)
        temp_control.setSuffix(" °C")
        self.components['temperature'] = temp_control
        layout.addWidget(temp_control, 1, 1)

        temp_label = QLabel("温度: 22.5°C")
        temp_control.valueChanged.connect(
            lambda v: temp_label.setText(f"温度: {v}°C"))
        layout.addWidget(temp_label, 1, 2)

        # 3. 价格输入
        layout.addWidget(QLabel("💰 价格输入:"), 2, 0)
        price_control = FluentDoubleSpinBox()
        price_control.setRange(0.01, 9999.99)
        price_control.setValue(99.99)
        price_control.setDecimals(2)
        price_control.setSingleStep(0.01)
        price_control.setPrefix("¥ ")
        self.components['price'] = price_control
        layout.addWidget(price_control, 2, 1)

        price_label = QLabel("价格: ¥99.99")
        price_control.valueChanged.connect(
            lambda v: price_label.setText(f"价格: ¥{v:.2f}"))
        layout.addWidget(price_label, 2, 2)

        # 4. 时间设置
        layout.addWidget(QLabel("⏰ 时间设置:"), 3, 0)
        time_layout = QHBoxLayout()

        hour_spin = FluentSpinBox()
        hour_spin.setRange(0, 23)
        hour_spin.setValue(14)
        hour_spin.setSuffix("时")
        self.components['hour'] = hour_spin

        minute_spin = FluentSpinBox()
        minute_spin.setRange(0, 59)
        minute_spin.setValue(30)
        minute_spin.setSuffix("分")
        self.components['minute'] = minute_spin

        time_layout.addWidget(hour_spin)
        time_layout.addWidget(minute_spin)
        layout.addLayout(time_layout, 3, 1)

        time_label = QLabel("时间: 14:30")

        def update_time():
            time_label.setText(
                f"时间: {hour_spin.value():02d}:{minute_spin.value():02d}")
        hour_spin.valueChanged.connect(lambda: update_time())
        minute_spin.valueChanged.connect(lambda: update_time())
        layout.addWidget(time_label, 3, 2)

        # 5. 数量选择
        layout.addWidget(QLabel("📦 数量选择:"), 4, 0)
        quantity_control = FluentNumberInput(
            minimum=1, maximum=999, decimals=0, step=1)
        quantity_control.set_value(1)
        self.components['quantity'] = quantity_control
        layout.addWidget(quantity_control, 4, 1)

        quantity_label = QLabel("数量: 1 件")
        quantity_control.value_changed.connect(
            lambda v: quantity_label.setText(f"数量: {int(v)} 件")
        )
        layout.addWidget(quantity_label, 4, 2)

        return group

    def _connect_signals(self):
        """连接信号"""
        # 为所有组件添加通用的变化监听
        for name, component in self.components.items():
            if hasattr(component, 'valueChanged'):
                component.valueChanged.connect(
                    lambda value, n=name: self._on_component_changed(n, value)
                )
            elif hasattr(component, 'value_changed'):
                component.value_changed.connect(
                    lambda value, n=name: self._on_component_changed(n, value)
                )

    def _on_component_changed(self, name: str, value):
        """组件值变化处理"""
        print(f"组件 {name} 值变化: {value}")

    def _on_theme_changed(self, state):
        """主题切换"""
        if state == Qt.CheckState.Checked:
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)

    def _toggle_demo(self):
        """切换演示模式"""
        if self.demo_timer.isActive():
            self.demo_timer.stop()
            self.demo_button.setText("开始动画演示")
        else:
            self.demo_timer.start(2000)  # 每2秒更新一次
            self.demo_button.setText("停止动画演示")

    def _update_demo_values(self):
        """更新演示值"""
        import random

        # 随机更新一些组件的值
        if 'animated' in self.components:
            value = random.randint(0, 100)
            self.components['animated'].set_value_animated(value)

        if 'precision' in self.components:
            value = random.uniform(0.0, 1.0)
            self.components['precision'].set_value_animated(value)

        if 'volume' in self.components:
            value = random.randint(0, 100)
            self.components['volume'].set_value(value)

    def _reset_all_values(self):
        """重置所有值"""
        # 重置所有组件到默认值
        default_values = {
            'basic_int': 50,
            'basic_double': 5.0,
            'negative': 0,
            'large': 50000,
            'animated': 0,
            'precision': 0.5,
            'step': 100,
            'wheel': 50,
            'keyboard': 50,
            'disabled': 50,
            'readonly': 75,
            'number1': 25,
            'number2': 5.0,
            'number3': 250,
            'number4': 0.5,
            'volume': 75,
            'temperature': 22.5,
            'price': 99.99,
            'hour': 14,
            'minute': 30,
            'quantity': 1
        }

        for name, value in default_values.items():
            if name in self.components:
                component = self.components[name]
                if hasattr(component, 'set_value_animated'):
                    component.set_value_animated(value)
                elif hasattr(component, 'set_value'):
                    component.set_value(value)
                elif hasattr(component, 'setValue'):
                    component.setValue(value)


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle('Fusion')

    # 创建并显示窗口
    window = SpinBoxDemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
