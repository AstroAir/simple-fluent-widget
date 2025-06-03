"""
 Fluent Card Components Demo
Showcasing enhanced performance, smooth animations, and consistent theming
"""

import sys
import time
import psutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QGridLayout, QLabel,
                               QScrollArea, QLineEdit, QComboBox,
                               QSpinBox, QSlider,
                               QFileDialog, QTabWidget)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor
from PySide6.QtCore import Slot

# Import the card components
from components.basic import FluentCard
from components.basic.button import FluentButton
from core.theme import theme_manager, ThemeMode


class PerformanceMonitor(QThread):
    """Monitor performance metrics during animations"""
    performanceUpdate = Signal(dict)

    def __init__(self):
        super().__init__()
        self.running = True
        self.fps_counter = 0
        self.start_time = 0

    def run(self):
        while self.running:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()

            metrics = {
                'cpu': cpu_percent,
                'memory': memory_info.percent,
                'memory_mb': memory_info.used / 1024 / 1024
            }

            self.performanceUpdate.emit(metrics)
            time.sleep(0.5)

    def stop(self):
        self.running = False


class CardDemo(QMainWindow):
    """Main demo window showcasing card features and performance"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            " Fluent Card Components Demo - Enhanced Performance")
        self.setGeometry(100, 100, 1600, 1000)

        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        self.performance_monitor.performanceUpdate.connect(
            self.update_performance_metrics)
        self.performance_monitor.start()

        # Central widget with scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setCentralWidget(scroll_area)

        # Main layout with spacing
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Enhanced title with performance info
        self._setup_header(main_layout)

        # Theme and performance controls
        self._setup_controls(main_layout)

        # Tab widget for organized demo sections
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Basic cards tab
        tab_widget.addTab(self._create_basic_cards_tab(), "Basic Cards")
        tab_widget.addTab(self._create_clickable_cards_tab(),
                          "Clickable Cards")

        # Image cards tab
        tab_widget.addTab(self._create_image_cards_tab(), "Image Cards")

        # Action cards tab
        tab_widget.addTab(self._create_action_cards_tab(), "Action Cards")

        # Info cards tab
        tab_widget.addTab(self._create_info_cards_tab(), "Info Cards")

        # Performance test tab
        tab_widget.addTab(self._create_performance_test_tab(),
                          "Performance Test")

        # Apply theme
        self._apply_theme()

    def _setup_header(self, layout):
        """Setup enhanced header with performance indicators"""
        header_layout = QVBoxLayout()

        # Main title
        title = QLabel(" Fluent Card Components Demo")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        # Performance indicators
        self.performance_label = QLabel(
            "Performance: CPU: 0% | Memory: 0% | FPS: 60")
        self.performance_label.setFont(QFont("Segoe UI", 10))
        self.performance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.performance_label.setStyleSheet("color: #888; padding: 5px;")
        header_layout.addWidget(self.performance_label)

        layout.addLayout(header_layout)

    def _setup_controls(self, layout):
        """Setup theme and performance controls"""
        controls_card = FluentCard()
        controls_layout = QHBoxLayout()

        # Theme controls
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)

        # Animation speed control
        speed_label = QLabel("Animation Speed:")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)

        controls_layout.addWidget(theme_label)
        controls_layout.addWidget(self.theme_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(speed_label)
        controls_layout.addWidget(self.speed_slider)

        controls_card.addLayout(controls_layout)
        layout.addWidget(controls_card)

    def _create_basic_cards_tab(self):
        """Create basic cards demonstration tab"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(15)

        # Basic card
        basic_card = FluentCard()
        content_layout = QVBoxLayout()
        content_layout.addWidget(QLabel("Basic Card"))
        content_layout.addWidget(QLabel("Simple card layout"))
        basic_card.addLayout(content_layout)
        layout.addWidget(basic_card, 0, 0)

        return widget

    def _create_clickable_cards_tab(self):
        """Create clickable and elevation cards demonstration tab"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(15)

        # Clickable card demo
        clickable_card = FluentCard()
        clickable_card.setClickable(True)
        clickable_card.setCornerRadius(12)
        clickable_card.setElevation(2)
        clickable_card.setHoverElevation(6)

        # Create content layout
        content_layout = QVBoxLayout()
        content_layout.addWidget(QLabel("Clickable Card"))
        content_layout.addWidget(QLabel("Hover and click to see animations"))
        clickable_card.addLayout(content_layout)
        clickable_card.clicked.connect(
            lambda: self._show_toast("Card clicked!"))

        layout.addWidget(clickable_card, 0, 0)

        # Different elevation cards
        for i, elevation in enumerate([1, 3, 6, 10]):
            card = FluentCard()
            card.setElevation(elevation)
            card.setCornerRadius(8 + i * 2)

            content_layout = QVBoxLayout()
            content_layout.addWidget(QLabel(f"Elevation {elevation}"))
            content_layout.addWidget(QLabel("shadow rendering"))
            card.addLayout(content_layout)

            layout.addWidget(card, 0, i + 1)

        # Interactive properties card
        props_card = FluentCard()
        props_layout = QVBoxLayout()

        props_layout.addWidget(QLabel("Interactive Properties"))

        # Elevation control
        elevation_layout = QHBoxLayout()
        elevation_layout.addWidget(QLabel("Elevation:"))
        elevation_spin = QSpinBox()
        elevation_spin.setRange(0, 20)
        elevation_spin.setValue(2)
        elevation_spin.valueChanged.connect(
            lambda v: props_card.setElevation(v))
        elevation_layout.addWidget(elevation_spin)
        props_layout.addLayout(elevation_layout)

        # Corner radius control
        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("Corner Radius:"))
        radius_spin = QSpinBox()
        radius_spin.setRange(0, 30)
        radius_spin.setValue(8)
        radius_spin.valueChanged.connect(
            lambda v: props_card.setCornerRadius(v))
        radius_layout.addWidget(radius_spin)
        props_layout.addLayout(radius_layout)

        props_card.addLayout(props_layout)
        layout.addWidget(props_card, 1, 0, 1, 3)

        return widget

    def _create_image_cards_tab(self):
        """Create image cards demonstration tab"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(15)

        # Create sample images
        sample_images = self._create_sample_images()

        for i, (name, pixmap) in enumerate(sample_images.items()):
            card = FluentCard()
            card.setClickable(True)

            content_layout = QVBoxLayout()
            content_layout.addWidget(QLabel(f"Image Card: {name}"))
            content_layout.addWidget(QLabel("image scaling and transitions"))
            card.addLayout(content_layout)

            card.clicked.connect(
                lambda n=name: self._show_toast(f"Clicked {n} card"))

            row, col = divmod(i, 3)
            layout.addWidget(card, row, col)

        # Interactive image card
        interactive_card = FluentCard()
        interactive_layout = QVBoxLayout()

        # Image height control
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Image Height:"))
        height_slider = QSlider(Qt.Orientation.Horizontal)
        height_slider.setRange(100, 300)
        height_slider.setValue(180)
        height_layout.addWidget(height_slider)
        interactive_layout.addLayout(height_layout)

        # Image selection
        select_btn = FluentButton("Select Image")
        select_btn.clicked.connect(
            lambda: self._select_image(interactive_card))
        interactive_layout.addWidget(select_btn)

        clear_btn = FluentButton("Clear Image")
        interactive_layout.addWidget(clear_btn)

        interactive_card.addLayout(interactive_layout)
        layout.addWidget(interactive_card, 2, 0, 1, 3)

        return widget

    def _create_action_cards_tab(self):
        """Create action cards demonstration tab"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(15)

        # Basic action card
        action_card = FluentCard()
        content_layout = QVBoxLayout()
        content_layout.addWidget(QLabel("Action Card"))
        content_layout.addWidget(QLabel("With action buttons"))

        # Add action buttons at bottom
        btn_layout = QHBoxLayout()
        primary_btn = FluentButton("Primary Action")
        secondary_btn = FluentButton("Secondary")
        secondary_btn.setProperty("style", "secondary")
        btn_layout.addWidget(primary_btn)
        btn_layout.addWidget(secondary_btn)
        content_layout.addLayout(btn_layout)

        action_card.addLayout(content_layout)
        layout.addWidget(action_card, 0, 0)

        # Multi-action card
        multi_card = FluentCard()
        content_layout = QVBoxLayout()
        content_layout.addWidget(QLabel("Multiple Actions"))
        content_layout.addWidget(QLabel("Test action management"))

        # Add multiple buttons
        btn_layout = QHBoxLayout()
        for i in range(3):
            btn = FluentButton(f"Action {i+1}")
            btn_layout.addWidget(btn)
        content_layout.addLayout(btn_layout)

        multi_card.addLayout(content_layout)
        layout.addWidget(multi_card, 0, 1)

        # Dynamic action card
        dynamic_card = FluentCard()
        content_layout = QVBoxLayout()
        content_layout.addWidget(QLabel("Dynamic Actions"))

        control_layout = QHBoxLayout()
        add_btn = FluentButton("Add Action")
        remove_btn = FluentButton("Remove Action")
        clear_btn = FluentButton("Clear All")

        self.action_counter = 0

        def add_action():
            self.action_counter += 1
            btn = FluentButton(f"Dynamic {self.action_counter}")
            control_layout.addWidget(btn)

        def remove_action():
            if control_layout.count() > 3:
                item = control_layout.takeAt(control_layout.count() - 1)
                if item and item.widget():
                    item.widget().deleteLater()

        add_btn.clicked.connect(add_action)
        remove_btn.clicked.connect(remove_action)

        control_layout.addWidget(add_btn)
        control_layout.addWidget(remove_btn)
        control_layout.addWidget(clear_btn)
        content_layout.addLayout(control_layout)

        dynamic_card.addLayout(content_layout)
        layout.addWidget(dynamic_card, 1, 0, 1, 2)

        return widget

    def _create_info_cards_tab(self):
        """Create info cards demonstration tab"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(15)

        # Basic info card
        info_card = FluentCard()
        content_layout = QVBoxLayout()
        content_layout.addWidget(QLabel("Info Card"))
        content_layout.addWidget(QLabel("Display information"))
        info_card.addLayout(content_layout)
        layout.addWidget(info_card, 0, 0)

        # Interactive info card
        interactive_info = FluentCard()
        edit_layout = QVBoxLayout()

        # Title editing
        title_edit = QLineEdit("Custom Info")
        edit_layout.addWidget(QLabel("Title:"))
        edit_layout.addWidget(title_edit)

        # Subtitle editing
        subtitle_edit = QLineEdit("Edit properties below")
        edit_layout.addWidget(QLabel("Subtitle:"))
        edit_layout.addWidget(subtitle_edit)

        # Icon editing
        icon_edit = QLineEdit("✏️")
        edit_layout.addWidget(QLabel("Icon:"))
        edit_layout.addWidget(icon_edit)

        interactive_info.addLayout(edit_layout)
        layout.addWidget(interactive_info, 0, 1)

        return widget

    def _create_performance_test_tab(self):
        """Create performance testing tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Performance test controls
        test_card = FluentCard()
        test_layout = QVBoxLayout()

        test_layout.addWidget(QLabel("Performance Testing"))
        test_layout.addWidget(QLabel("Test animations and rendering"))

        # Test controls
        controls_layout = QHBoxLayout()

        # Number of cards to create
        count_spin = QSpinBox()
        count_spin.setRange(1, 100)
        count_spin.setValue(20)

        # Animation type
        animation_combo = QComboBox()
        animation_combo.addItems(["Entrance", "Hover", "Click", "All"])

        # Test button
        test_btn = FluentButton("Run Performance Test")
        test_btn.clicked.connect(lambda: self._run_performance_test(
            count_spin.value(), animation_combo.currentText()))

        controls_layout.addWidget(QLabel("Card Count:"))
        controls_layout.addWidget(count_spin)
        controls_layout.addWidget(QLabel("Animation:"))
        controls_layout.addWidget(animation_combo)
        controls_layout.addWidget(test_btn)

        test_layout.addLayout(controls_layout)
        test_card.addLayout(test_layout)
        layout.addWidget(test_card)

        # Performance results area
        self.results_area = QScrollArea()
        self.results_widget = QWidget()
        self.results_layout = QGridLayout(self.results_widget)
        self.results_area.setWidget(self.results_widget)
        self.results_area.setWidgetResizable(True)
        layout.addWidget(self.results_area)

        return widget

    def _create_sample_images(self):
        """Create sample images for demonstration"""
        images = {}
        colors = [
            ("#FF6B6B", "Red Gradient"),
            ("#4ECDC4", "Teal Gradient"),
            ("#45B7D1", "Blue Gradient"),
            ("#96CEB4", "Green Gradient")
        ]

        for color, name in colors:
            pixmap = QPixmap(300, 200)
            painter = QPainter(pixmap)
            painter.fillRect(pixmap.rect(), QColor(color))
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, name)
            painter.end()
            images[name] = pixmap

        return images

    def _apply_theme(self):
        """Apply theme settings"""
        pass

    def _on_theme_changed(self, theme_name):
        """Handle theme change"""
        if theme_name.lower() == "dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)

        self._show_toast(f"Theme changed to {theme_name}")

    def _on_speed_changed(self, value):
        """Handle animation speed change"""
        speed_factor = value / 100.0
        self._show_toast(f"Animation speed: {value}%")

    def _run_performance_test(self, count, animation_type):
        """Run performance test with specified parameters"""
        # Clear previous results
        for i in reversed(range(self.results_layout.count())):
            item = self.results_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        # Create test cards
        start_time = time.time()

        for i in range(count):
            card = FluentCard()
            card.setClickable(True)

            content_layout = QVBoxLayout()
            content_layout.addWidget(QLabel(f"Test Card {i+1}"))
            content_layout.addWidget(QLabel(f"Animation: {animation_type}"))
            card.addLayout(content_layout)

            if animation_type in ["Hover", "All"]:
                card.setHoverElevation(8)

            if animation_type in ["Click", "All"]:
                card.clicked.connect(
                    lambda i=i: self._show_toast(f"Card {i+1} clicked"))

            row, col = divmod(i, 4)
            self.results_layout.addWidget(card, row, col)

        creation_time = time.time() - start_time
        self._show_toast(f"Created {count} cards in {creation_time:.2f}s")

    def _select_image(self, card):
        """Select image for image card"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self._show_toast("Image loaded successfully")

    def _show_toast(self, message):
        """Show toast notification"""
        self.statusBar().showMessage(message, 3000)

    @Slot(object)
    def update_performance_metrics(self, metrics):
        """Update performance metrics display"""
        cpu = metrics['cpu']
        memory = metrics['memory']
        memory_mb = metrics['memory_mb']
        self.performance_label.setText(
            f"Performance: CPU: {cpu:.1f}% | Memory: {memory:.1f}% ({memory_mb:.0f}MB)")
        # Update color based on performance
        if cpu > 80 or memory > 80:
            self.performance_label.setStyleSheet(
                "color: #ff4444; padding: 5px;")
        elif cpu > 60 or memory > 60:
            self.performance_label.setStyleSheet(
                "color: #ffaa00; padding: 5px;")
        else:
            self.performance_label.setStyleSheet(
                "color: #44aa44; padding: 5px;")

    def closeEvent(self, event):
        """Handle close event"""
        self.performance_monitor.stop()
        self.performance_monitor.wait()

        # Cleanup all cards
        def cleanup_widget(widget):
            for child in widget.findChildren(FluentCard):
                if hasattr(child, 'cleanup'):
                    child.cleanup()

        cleanup_widget(self)
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName(" Fluent Cards Demo")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Fluent UI")

    # Create and show demo window
    demo = CardDemo()
    demo.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
