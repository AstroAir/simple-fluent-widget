#!/usr/bin/env python3
"""
Fluent Components Comprehensive Demo
Demonstrates integrated usage of multiple Fluent layout components
"""

from components.layout.containers import (
    FluentCard, FluentExpander, FluentSplitter, FluentInfoBar, FluentPivot
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QListWidget, QTextEdit, QTreeWidgetItem, QTreeWidget
)
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Import Fluent components


class ComponentDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Components Demo")
        self.setGeometry(100, 100, 1000, 800)

        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create component sections
        self.create_pivot_navigation(main_layout)
        self.create_card_example(main_layout)
        self.create_expander_group(main_layout)

    def create_pivot_navigation(self, parent_layout):
        """Create pivot-controlled content area"""
        pivot = FluentPivot()

        # Pivot items with associated content
        content1 = self.create_sample_card("Dashboard Content")
        content2 = self.create_sample_list("Settings Options")
        content3 = self.create_editor_panel()

        pivot.addItem("Dashboard", content1)
        pivot.addItem("Settings", content2)
        pivot.addItem("Editor", content3)

        parent_layout.addWidget(pivot)

    def create_card_example(self, parent_layout):
        """Create an interactive FluentCard example"""
        card = FluentCard()
        card.setHeaderText("Interactive Card")

        card_layout = QVBoxLayout()

        # Card content
        info_bar = FluentInfoBar(
            "Info",
            "This card demonstrates component integration",
            severity=FluentInfoBar.Severity.INFO
        )

        btn = QPushButton("Toggle Expanders")
        btn.clicked.connect(self.toggle_all_expanders)

        card_layout.addWidget(info_bar)
        card_layout.addWidget(btn)
        card.addLayout(card_layout)

        parent_layout.addWidget(card)

    def create_expander_group(self, parent_layout):
        """Create a group of expanders in a splitter"""
        splitter = FluentSplitter(Qt.Orientation.Vertical)

        # Expander 1 - File Explorer
        expander1 = FluentExpander("File System")
        tree = QTreeWidget()
        tree.addTopLevelItem(QTreeWidgetItem(["Project Files"]))
        expander1.addWidget(tree)

        # Expander 2 - Console
        expander2 = FluentExpander("Output Console")
        console = QTextEdit()
        console.setMaximumHeight(150)
        expander2.addWidget(console)

        splitter.addWidget(expander1)
        splitter.addWidget(expander2)
        splitter.setSizes([400, 200])

        parent_layout.addWidget(splitter)

    def toggle_all_expanders(self):
        """Toggle all expanders in the layout"""
        for child in self.findChildren(FluentExpander):
            child.setExpanded(not child.isExpanded())

    # Helper methods for creating content widgets
    def create_sample_card(self, text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel(text))
        return widget

    def create_sample_list(self, title):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel(title))
        list_widget = QListWidget()
        list_widget.addItems(["Option 1", "Option 2", "Option 3"])
        layout.addWidget(list_widget)
        return widget

    def create_editor_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        editor = QTextEdit()
        editor.setPlainText("Sample editor content")
        layout.addWidget(editor)
        return widget


def main():
    app = QApplication(sys.argv)
    demo = ComponentDemo()
    demo.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
