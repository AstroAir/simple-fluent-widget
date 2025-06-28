#!/usr/bin/env python3
"""
Fluent Chip Component Demo

This example demonstrates the usage of FluentChip components with various configurations,
including different styles, types, sizes, and interactive features.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QGroupBox, QScrollArea
from PySide6.QtCore import Qt

from components.basic.display.chip import FluentChip
from core.theme import theme_manager


class ChipDemo(QMainWindow):
    """Main demo window showcasing Fluent chip components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Chip Demo")
        self.setGeometry(200, 200, 900, 700)
        
        # Create central widget with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title
        title = QLabel("Fluent Chip Components Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #323130; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Create demo sections
        self.create_basic_chips(main_layout)
        self.create_styled_chips(main_layout)
        self.create_interactive_chips(main_layout)
        self.create_size_variations(main_layout)
        
        main_layout.addStretch()
        
    def create_flow_layout(self, chips):
        """Create a horizontal layout for chips with wrapping."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for chip in chips:
            layout.addWidget(chip)
        
        layout.addStretch()
        return container
        
    def create_basic_chips(self, parent_layout):
        """Create basic chip examples."""
        group = QGroupBox("Basic Chips")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Default chips
        basic_chips = []
        
        # Basic chip
        basic_chip = FluentChip(text="Basic Chip")
        basic_chips.append(basic_chip)
        
        # Closable chip
        closable_chip = FluentChip(text="Closable", closable=True)
        basic_chips.append(closable_chip)
        
        # Non-clickable chip
        info_chip = FluentChip(text="Info Only", clickable=False)
        basic_chips.append(info_chip)
        
        # With icon
        icon_chip = FluentChip(text="With Icon", icon="⭐")
        basic_chips.append(icon_chip)
        
        layout.addWidget(QLabel("Default Style:"))
        layout.addWidget(self.create_flow_layout(basic_chips))
        
        parent_layout.addWidget(group)
        
    def create_styled_chips(self, parent_layout):
        """Create chips with different styles and types."""
        group = QGroupBox("Styled Chips")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Different chip types (filled style)
        filled_chips = []
        
        chip_types = [
            ("Default", FluentChip.ChipType.DEFAULT),
            ("Primary", FluentChip.ChipType.PRIMARY),
            ("Success", FluentChip.ChipType.SUCCESS),
            ("Warning", FluentChip.ChipType.WARNING),
            ("Error", FluentChip.ChipType.ERROR),
            ("Info", FluentChip.ChipType.INFO),
        ]
        
        for text, chip_type in chip_types:
            chip = FluentChip(
                text=text,
                chip_style=FluentChip.ChipStyle.FILLED,
                chip_type=chip_type
            )
            filled_chips.append(chip)
        
        layout.addWidget(QLabel("Filled Style - Different Types:"))
        layout.addWidget(self.create_flow_layout(filled_chips))
        layout.addSpacing(15)
        
        # Outlined style
        outlined_chips = []
        
        for text, chip_type in chip_types:
            chip = FluentChip(
                text=text,
                chip_style=FluentChip.ChipStyle.OUTLINED,
                chip_type=chip_type
            )
            outlined_chips.append(chip)
        
        layout.addWidget(QLabel("Outlined Style:"))
        layout.addWidget(self.create_flow_layout(outlined_chips))
        layout.addSpacing(15)
        
        # Text style
        text_chips = []
        
        for text, chip_type in chip_types:
            chip = FluentChip(
                text=text,
                chip_style=FluentChip.ChipStyle.TEXT,
                chip_type=chip_type
            )
            text_chips.append(chip)
        
        layout.addWidget(QLabel("Text Style:"))
        layout.addWidget(self.create_flow_layout(text_chips))
        
        parent_layout.addWidget(group)
        
    def create_interactive_chips(self, parent_layout):
        """Create interactive chip examples."""
        group = QGroupBox("Interactive Chips")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Clickable chips with feedback
        click_chips = []
        
        click_count = {"count": 0}
        status_label = QLabel("Click count: 0")
        
        def handle_chip_click():
            click_count["count"] += 1
            status_label.setText(f"Click count: {click_count['count']}")
        
        click_chip_texts = [
            "Click Me",
            "Me Too!",
            "And Me!",
        ]
        
        for chip_text in click_chip_texts:
            chip = FluentChip(text=chip_text, chip_type=FluentChip.ChipType.PRIMARY)
            chip.clicked.connect(handle_chip_click)
            click_chips.append(chip)
        
        layout.addWidget(QLabel("Clickable Chips:"))
        layout.addWidget(self.create_flow_layout(click_chips))
        layout.addWidget(status_label)
        layout.addSpacing(15)
        
        # Removable chips
        removable_chips = []
        removed_count = {"count": 0}
        removed_label = QLabel("Removed chips: 0")
        
        def handle_chip_remove():
            removed_count["count"] += 1
            removed_label.setText(f"Removed chips: {removed_count['count']}")
        
        removable_chip_texts = [
            "Remove Me",
            "Delete This",
            "Close Me",
            "Dismiss",
        ]
        
        for chip_text in removable_chip_texts:
            chip = FluentChip(text=chip_text, closable=True, chip_type=FluentChip.ChipType.WARNING)
            chip.close_clicked.connect(handle_chip_remove)
            removable_chips.append(chip)
        
        layout.addWidget(QLabel("Removable Chips (click X to remove):"))
        layout.addWidget(self.create_flow_layout(removable_chips))
        layout.addWidget(removed_label)
        
        parent_layout.addWidget(group)
        
    def create_size_variations(self, parent_layout):
        """Create chips with different sizes."""
        group = QGroupBox("Size Variations")
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        layout = QVBoxLayout(group)
        
        # Different sizes
        size_chips = []
        
        sizes = [
            ("Small", FluentChip.ChipSize.SMALL),
            ("Medium", FluentChip.ChipSize.MEDIUM),
            ("Large", FluentChip.ChipSize.LARGE),
        ]
        
        for text, size in sizes:
            chip = FluentChip(
                text=text,
                size=size,
                chip_type=FluentChip.ChipType.INFO
            )
            size_chips.append(chip)
        
        layout.addWidget(QLabel("Different Sizes:"))
        layout.addWidget(self.create_flow_layout(size_chips))
        layout.addSpacing(15)
        
        # Same text, different sizes for comparison
        comparison_chips = []
        
        for text, size in sizes:
            chip = FluentChip(
                text="Sample Text",
                size=size,
                chip_style=FluentChip.ChipStyle.OUTLINED,
                chip_type=FluentChip.ChipType.PRIMARY
            )
            comparison_chips.append(chip)
        
        layout.addWidget(QLabel("Size Comparison (Same Text):"))
        layout.addWidget(self.create_flow_layout(comparison_chips))
        
        # Tags example
        tags_chips = []
        tags = ["Python", "JavaScript", "React", "Qt", "UI/UX", "Design", "Backend", "Frontend"]
        
        for i, tag in enumerate(tags):
            size = [FluentChip.ChipSize.SMALL, FluentChip.ChipSize.MEDIUM, FluentChip.ChipSize.LARGE][i % 3]
            chip_type = [FluentChip.ChipType.PRIMARY, FluentChip.ChipType.SUCCESS, FluentChip.ChipType.INFO][i % 3]
            
            chip = FluentChip(
                text=tag,
                size=size,
                chip_type=chip_type,
                closable=True
            )
            tags_chips.append(chip)
        
        layout.addWidget(QLabel("Mixed Size Tags:"))
        layout.addWidget(self.create_flow_layout(tags_chips))
        
        parent_layout.addWidget(group)


def main():
    """Run the chip demo application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Fluent Chip Demo")
    app.setApplicationVersion("1.0.0")
    
    # Create and show demo window
    demo = ChipDemo()
    demo.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
