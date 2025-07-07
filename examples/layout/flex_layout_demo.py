#!/usr/bin/env python3
"""
Fluent Flex Layout Comprehensive Demo
Demonstrates advanced flex layout capabilities with dynamic controls
"""

from components.layout.flex_layout import (
    FluentFlexLayout, FlexDirection, FlexWrap,
    JustifyContent, AlignItems, AlignContent
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QSpinBox, QLabel, QFrame, QSlider
)
import sys
from pathlib import Path
from random import randint

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class FlexLayoutDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Flex Layout Demo")
        self.setGeometry(100, 100, 1200, 800)

        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create controls
        self.create_controls(main_layout)

        # Create flex layout container
        self.create_flex_container(main_layout)

        # Initial items
        self.add_flex_item()
        self.add_flex_item()

    def create_controls(self, parent_layout):
        """Create control panel for flex properties"""
        control_card = QFrame()
        control_layout = QHBoxLayout(control_card)

        # Direction selector
        self.dir_combo = QComboBox()
        self.dir_combo.addItems([d.name for d in FlexDirection])
        self.dir_combo.currentIndexChanged.connect(self.update_flex_layout)

        # Justify content
        self.justify_combo = QComboBox()
        self.justify_combo.addItems([j.name for j in JustifyContent])
        self.justify_combo.currentIndexChanged.connect(self.update_flex_layout)

        # Align items
        self.align_combo = QComboBox()
        self.align_combo.addItems([a.name for a in AlignItems])
        self.align_combo.currentIndexChanged.connect(self.update_flex_layout)

        # Gap controls
        self.gap_spin = QSpinBox()
        self.gap_spin.setRange(0, 50)
        self.gap_spin.valueChanged.connect(self.update_flex_layout)

        # Item controls
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_flex_item)
        remove_btn = QPushButton("Remove Item")
        remove_btn.clicked.connect(self.remove_flex_item)

        control_layout.addWidget(QLabel("Direction:"))
        control_layout.addWidget(self.dir_combo)
        control_layout.addWidget(QLabel("Justify:"))
        control_layout.addWidget(self.justify_combo)
        control_layout.addWidget(QLabel("Align:"))
        control_layout.addWidget(self.align_combo)
        control_layout.addWidget(QLabel("Gap:"))
        control_layout.addWidget(self.gap_spin)
        control_layout.addWidget(add_btn)
        control_layout.addWidget(remove_btn)

        parent_layout.addWidget(control_card)

    def create_flex_container(self, parent_layout):
        """Create the flex layout container"""
        self.flex_layout = FluentFlexLayout()
        # self.flex_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinAndMaxSize)

        container = QWidget()
        # FluentFlexLayout 不是 QLayout，不能直接 setLayout
        # 解决方法：将 flex_layout 作为 QWidget 的子类，或直接将 flex_layout 作为主容器
        # 这里直接将 flex_layout 作为 main_layout 的子布局
        main_layout = parent_layout
        main_layout.addLayout(self.flex_layout)
        container.setStyleSheet(
            "background-color: #f3f2f1; border: 1px solid #edebe9;")

        parent_layout.addWidget(container)

    def add_flex_item(self):
        """Add a new flex item with random properties"""
        item = QFrame()
        item.setMinimumSize(100, 60)

        # Random flex properties
        grow = randint(0, 2)
        shrink = randint(0, 2)
        basis = randint(100, 200) if randint(0, 1) else "auto"

        # Visual styling
        color = QColor(randint(100, 255), randint(100, 255), randint(100, 255))
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {color.name()};
                border: 1px solid #ffffff;
                border-radius: 4px;
            }}
        """)

        # Add label with properties
        layout = QVBoxLayout(item)
        layout.addWidget(
            QLabel(f"Grow: {grow}\nShrink: {shrink}\nBasis: {basis}"))

        # Add to flex layout with properties
        self.flex_layout.add_widget(
            item,
            flex_grow=grow,
            flex_shrink=shrink,
            flex_basis=basis,
            align_self=AlignItems.CENTER
        )

    def remove_flex_item(self):
        """Remove last added flex item"""
        # FluentFlexLayout 没有 count/itemAt，需遍历 _flex_items
        if hasattr(self.flex_layout, "_flex_items") and self.flex_layout._flex_items:
            item = self.flex_layout._flex_items[-1].widget
            self.flex_layout.remove_widget(item)
            item.deleteLater()

    def update_flex_layout(self):
        """Update flex properties from controls"""
        self.flex_layout.set_flex_direction(
            FlexDirection(self.dir_combo.currentText()))
        self.flex_layout.set_justify_content(
            JustifyContent(self.justify_combo.currentText()))
        self.flex_layout.set_align_items(
            AlignItems(self.align_combo.currentText()))
        self.flex_layout.set_gap(self.gap_spin.value())


def main():
    app = QApplication(sys.argv)
    demo = FlexLayoutDemo()
    demo.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
