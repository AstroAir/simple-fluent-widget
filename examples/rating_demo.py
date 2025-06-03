"""
Enhanced Rating Component Demo
Demonstrates all the advanced features and improvements of the enhanced rating component.
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QWidget, QLabel, QPushButton, QSlider, QComboBox,
                               QCheckBox, QGroupBox, QSpinBox, QTextEdit, QFrame,
                               QGridLayout, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette, QColor

from components.basic.rating_enhanced import EnhancedFluentRating
from core.theme import theme_manager, ThemeMode


class RatingDemoWidget(QWidget):
    """Demo widget showcasing enhanced rating features"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enhanced Fluent Rating Component Demo")
        self.setMinimumSize(900, 700)

        # Demo components
        self.ratings = []
        self.setup_ui()
        self.setup_demo_scenarios()

    def setup_ui(self):
        """Setup the demo UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Enhanced Fluent Rating Component")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel(
            "Demonstrating modern PySide6 features with smooth animations and responsive design")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666666; margin-bottom: 20px;")
        main_layout.addWidget(subtitle)

        # Create demo sections
        self.create_basic_features_section(main_layout)
        self.create_animation_showcase_section(main_layout)
        self.create_customization_section(main_layout)
        self.create_interactive_controls_section(main_layout)

        # Status area
        self.create_status_section(main_layout)

    def create_basic_features_section(self, parent_layout):
        """Create basic features demonstration"""
        group = QGroupBox("Basic Features & Responsive Design")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Different rating configurations
        configs = [
            ("Default Rating (5 stars)", 5, 3, True, "star"),
            ("Large Rating (7 stars)", 7, 4, True, "star"),
            ("Read-only Rating", 5, 5, False, "star"),
            ("Heart Style Rating", 5, 2, True, "heart"),
            ("Thumb Style Rating", 5, 1, True, "thumb"),
        ]

        for label_text, max_rating, current, editable, style in configs:
            row_layout = QHBoxLayout()

            label = QLabel(label_text)
            label.setMinimumWidth(200)
            label.setFont(QFont("Segoe UI", 10))

            rating = EnhancedFluentRating()
            rating.setMaxRating(max_rating)
            rating.setRating(current)
            rating.setEditable(editable)
            rating.setStarStyle(style)

            # Connect signals for demo
            rating.ratingChanged.connect(
                lambda r, lt=label_text: self.on_rating_changed(lt, r)
            )
            rating.hoverChanged.connect(
                lambda h, lt=label_text: self.on_hover_changed(lt, h)
            )

            self.ratings.append(rating)

            row_layout.addWidget(label)
            row_layout.addWidget(rating)
            row_layout.addStretch()

            layout.addLayout(row_layout)

        parent_layout.addWidget(group)

    def create_animation_showcase_section(self, parent_layout):
        """Create animation showcase section"""
        group = QGroupBox("Animation & Micro-interactions")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Special ratings for animation demo
        demo_layout = QHBoxLayout()

        # Celebration rating (high values trigger special animations)
        celebration_label = QLabel("Celebration Effects:")
        celebration_label.setFont(QFont("Segoe UI", 10))

        self.celebration_rating = EnhancedFluentRating()
        self.celebration_rating.setMaxRating(5)
        self.celebration_rating.setRating(0)
        self.celebration_rating.ratingChanged.connect(
            self.on_celebration_rating_changed)

        demo_layout.addWidget(celebration_label)
        demo_layout.addWidget(self.celebration_rating)
        demo_layout.addStretch()

        layout.addLayout(demo_layout)

        # Animation control buttons
        button_layout = QHBoxLayout()

        animate_btn = QPushButton("Trigger Celebration (5 stars)")
        animate_btn.clicked.connect(
            lambda: self.celebration_rating.setRating(5))

        reset_btn = QPushButton("Reset to 0")
        reset_btn.clicked.connect(lambda: self.celebration_rating.setRating(0))

        pulse_btn = QPushButton("Manual Pulse Effect")
        pulse_btn.clicked.connect(self.trigger_pulse_effect)

        button_layout.addWidget(animate_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(pulse_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Performance note
        perf_note = QLabel("• Animations are optimized with 60 FPS updates and memory-efficient caching"
                           "\\n• Smooth easing curves provide natural motion feel"
                           "\\n• Micro-interactions respond to hover, press, and rating changes")
        perf_note.setFont(QFont("Segoe UI", 9))
        perf_note.setStyleSheet("color: #666666; margin-top: 10px;")
        layout.addWidget(perf_note)

        parent_layout.addWidget(group)

    def create_customization_section(self, parent_layout):
        """Create customization controls section"""
        group = QGroupBox("Dynamic Customization & Theme Integration")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QGridLayout(group)

        # Sample rating for customization
        self.custom_rating = EnhancedFluentRating()
        self.custom_rating.setMaxRating(5)
        self.custom_rating.setRating(3)

        layout.addWidget(QLabel("Sample Rating:"), 0, 0)
        layout.addWidget(self.custom_rating, 0, 1, 1, 2)

        # Star size control
        layout.addWidget(QLabel("Star Size:"), 1, 0)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(16, 64)
        self.size_slider.setValue(32)
        self.size_slider.valueChanged.connect(self.on_size_changed)
        layout.addWidget(self.size_slider, 1, 1)

        self.size_label = QLabel("32px")
        layout.addWidget(self.size_label, 1, 2)

        # Max rating control
        layout.addWidget(QLabel("Max Rating:"), 2, 0)
        self.max_rating_spin = QSpinBox()
        self.max_rating_spin.setRange(3, 10)
        self.max_rating_spin.setValue(5)
        self.max_rating_spin.valueChanged.connect(self.on_max_rating_changed)
        layout.addWidget(self.max_rating_spin, 2, 1)

        # Style control
        layout.addWidget(QLabel("Style:"), 3, 0)
        self.style_combo = QComboBox()
        self.style_combo.addItems(["star", "heart", "thumb"])
        self.style_combo.currentTextChanged.connect(self.on_style_changed)
        layout.addWidget(self.style_combo, 3, 1)

        # Editable control
        self.editable_check = QCheckBox("Editable")
        self.editable_check.setChecked(True)
        self.editable_check.toggled.connect(self.on_editable_changed)
        layout.addWidget(self.editable_check, 4, 0)

        # Theme control
        layout.addWidget(QLabel("Theme:"), 5, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_combo, 5, 1)

        parent_layout.addWidget(group)

    def create_interactive_controls_section(self, parent_layout):
        """Create interactive controls demonstration"""
        group = QGroupBox("Accessibility & Keyboard Navigation")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        # Keyboard navigation demo
        kb_layout = QHBoxLayout()
        kb_label = QLabel("Keyboard Navigation:")
        kb_label.setFont(QFont("Segoe UI", 10))

        self.keyboard_rating = EnhancedFluentRating()
        self.keyboard_rating.setMaxRating(5)
        self.keyboard_rating.setRating(2)
        self.keyboard_rating.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        kb_layout.addWidget(kb_label)
        kb_layout.addWidget(self.keyboard_rating)
        kb_layout.addStretch()

        layout.addLayout(kb_layout)

        # Instructions
        instructions = QLabel(
            "• Click to focus, then use arrow keys or number keys (1-5) to change rating\\n"
            "• Tab to navigate between components\\n"
            "• Screen reader support with accessible descriptions"
        )
        instructions.setFont(QFont("Segoe UI", 9))
        instructions.setStyleSheet("color: #666666; margin-top: 10px;")
        layout.addWidget(instructions)

        parent_layout.addWidget(group)

    def create_status_section(self, parent_layout):
        """Create status display section"""
        group = QGroupBox("Event Monitoring & Performance Status")
        group.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)

        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(150)
        self.status_text.setFont(QFont("Consolas", 9))
        self.status_text.setReadOnly(True)

        layout.addWidget(self.status_text)

        # Clear button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.status_text.clear)
        layout.addWidget(clear_btn)

        parent_layout.addWidget(group)

    def setup_demo_scenarios(self):
        """Setup automated demo scenarios"""
        # Auto-demo timer
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.run_auto_demo)
        self.demo_step = 0

        # Start auto demo after 3 seconds
        QTimer.singleShot(3000, self.start_auto_demo)

    def start_auto_demo(self):
        """Start automated demonstration"""
        self.log_status("🚀 Starting automated demo showcase...")
        self.demo_timer.start(2000)  # Every 2 seconds

    def run_auto_demo(self):
        """Run automated demo steps"""
        demo_steps = [
            lambda: self.celebration_rating.setRating(1),
            lambda: self.celebration_rating.setRating(2),
            lambda: self.celebration_rating.setRating(3),
            lambda: self.celebration_rating.setRating(4),
            lambda: self.celebration_rating.setRating(
                5),  # Triggers celebration
            lambda: self.custom_rating.setStarStyle("heart"),
            lambda: self.custom_rating.setStarStyle("thumb"),
            lambda: self.custom_rating.setStarStyle("star"),
            lambda: self.size_slider.setValue(48),
            lambda: self.size_slider.setValue(32),
            lambda: self.demo_timer.stop(),
        ]

        if self.demo_step < len(demo_steps):
            demo_steps[self.demo_step]()
            self.demo_step += 1
        else:
            self.demo_timer.stop()
            self.log_status(
                "✅ Auto demo completed! Try interacting with the components.")

    # Event handlers
    def on_rating_changed(self, component_name, rating):
        """Handle rating change events"""
        self.log_status(f"📊 {component_name}: Rating changed to {rating}")

    def on_hover_changed(self, component_name, hover_rating):
        """Handle hover change events"""
        if hover_rating > 0:
            self.log_status(
                f"👆 {component_name}: Hovering over star {hover_rating}")

    def on_celebration_rating_changed(self, rating):
        """Handle celebration rating changes"""
        if rating >= 4:
            self.log_status(
                f"🎉 Celebration triggered! Rating: {rating} (watch the rotation animation)")
        else:
            self.log_status(f"⭐ Celebration rating: {rating}")

    def trigger_pulse_effect(self):
        """Trigger manual pulse effect"""
        from core.enhanced_animations import FluentMicroInteraction
        FluentMicroInteraction.pulse_animation(
            self.celebration_rating, scale=1.2)
        self.log_status("💫 Manual pulse effect triggered")

    def on_size_changed(self, size):
        """Handle star size changes"""
        self.custom_rating.setStarSize(size)
        self.size_label.setText(f"{size}px")
        self.log_status(f"📏 Star size changed to {size}px")

    def on_max_rating_changed(self, max_rating):
        """Handle max rating changes"""
        self.custom_rating.setMaxRating(max_rating)
        self.log_status(f"🔢 Max rating changed to {max_rating}")

    def on_style_changed(self, style):
        """Handle style changes"""
        self.custom_rating.setStarStyle(style)
        self.log_status(f"🎨 Style changed to {style}")

    def on_editable_changed(self, editable):
        """Handle editable state changes"""
        self.custom_rating.setEditable(editable)
        self.log_status(f"✏️ Editable: {editable}")

    def on_theme_changed(self, theme_name):
        """Handle theme changes"""
        if theme_manager:
            mode = ThemeMode.LIGHT if theme_name == "Light" else ThemeMode.DARK
            theme_manager.set_theme_mode(mode)
            self.log_status(f"🌓 Theme changed to {theme_name}")

    def log_status(self, message):
        """Log status message"""
        from PySide6.QtCore import QDateTime
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.status_text.append(f"[{timestamp}] {message}")

        # Auto-scroll to bottom
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class RatingDemoMainWindow(QMainWindow):
    """Main window for the rating demo"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Fluent Rating Component - Demo")
        self.setMinimumSize(1000, 800)

        # Set central widget
        self.demo_widget = RatingDemoWidget()
        self.setCentralWidget(self.demo_widget)

        # Apply styling
        self.setup_styling()

    def setup_styling(self):
        """Setup window styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f2f1;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #d1d1d1;
                border-radius: 8px;
                margin: 10px 0;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #323130;
                background-color: #f3f2f1;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QTextEdit {
                border: 1px solid #d1d1d1;
                border-radius: 4px;
                background-color: white;
                font-family: 'Consolas', monospace;
            }
        """)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Enhanced Fluent Rating Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Fluent UI Components")

    # Create and show main window
    window = RatingDemoMainWindow()
    window.show()

    # Center window on screen
    screen = app.primaryScreen().geometry()
    window_size = window.geometry()
    x = (screen.width() - window_size.width()) // 2
    y = (screen.height() - window_size.height()) // 2
    window.move(x, y)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
