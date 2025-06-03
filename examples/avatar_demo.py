#!/usr/bin/env python3
"""
 Avatar Component Demo
Comprehensive demonstration of the enhanced avatar features, animations, and capabilities.
"""

from components.basic.avatar import (FluentAvatar, FluentAvatarGroup,
                                     AvatarPresence, AvatarActivity)
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QWidget, QLabel, QPushButton, QSpinBox, QComboBox,
                               QCheckBox, QSlider, QGroupBox, QScrollArea, QFrame,
                               QGridLayout, QTextEdit)
from core.theme import theme_manager, ThemeMode
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtCore import Qt, QTimer, QSize
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class AvatarDemoWindow(QMainWindow):
    """Main demo window showcasing enhanced avatar features"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Fluent Avatar Demo")
        self.setGeometry(100, 100, 1200, 800)        # Setup theme
        theme_manager.set_theme_mode(ThemeMode.DARK)

        # Test avatars for reference
        self.test_avatars = []

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Create demo sections
        self.create_single_avatar_demo(layout)
        self.create_group_avatar_demo(layout)
        self.create_controls_panel(layout)
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.animate_demo)
        self.demo_timer.start(3000)  # Demo animations every 3 seconds

    def create_single_avatar_demo(self, parent_layout):
        """Create single avatar demonstration section"""
        group = QGroupBox("Single Avatar Features")
        group.setMinimumWidth(350)
        layout = QVBoxLayout(group)

        # Title
        title = QLabel(" Avatar Showcase")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Avatar sizes demo
        sizes_layout = QHBoxLayout()
        sizes_label = QLabel("Sizes:")
        sizes_layout.addWidget(sizes_label)

        for size in FluentAvatar.Size:
            avatar = FluentAvatar()
            avatar.setSize(size)
            avatar.setText("AB")
            avatar.setPresence(AvatarPresence.AVAILABLE)
            sizes_layout.addWidget(avatar)
            self.test_avatars.append(avatar)

        layout.addLayout(sizes_layout)

        # Shapes demo
        shapes_layout = QHBoxLayout()
        shapes_label = QLabel("Shapes:")
        shapes_layout.addWidget(shapes_label)
        
        shapes = ['circle', 'rounded_square', 'hexagon']
        for i, shape in enumerate(shapes):
            avatar = FluentAvatar()
            avatar.setSize(FluentAvatar.Size.LARGE)
            avatar.setText(f"S{i+1}")
            avatar.setShape(FluentAvatar.Shape(shape))
            avatar.setPresence(AvatarPresence.BUSY if i %
                               2 else AvatarPresence.AVAILABLE)
            shapes_layout.addWidget(avatar)
            self.test_avatars.append(avatar)

        layout.addLayout(shapes_layout)

        # Presence states demo
        presence_layout = QHBoxLayout()
        presence_label = QLabel("Presence:")
        presence_layout.addWidget(presence_label)

        for presence in AvatarPresence:
            if presence != AvatarPresence.NONE:
                avatar = FluentAvatar()
                avatar.setSize(FluentAvatar.Size.MEDIUM)
                avatar.setText("PS")
                avatar.setPresence(presence)
                presence_layout.addWidget(avatar)
                self.test_avatars.append(avatar)

        layout.addLayout(presence_layout)

        # Activity states demo
        activity_layout = QHBoxLayout()
        activity_label = QLabel("Activities:")
        activity_layout.addWidget(activity_label)

        for activity in AvatarActivity:
            if activity != AvatarActivity.NONE:
                avatar = FluentAvatar()
                avatar.setSize(FluentAvatar.Size.MEDIUM)
                avatar.setText("AC")
                avatar.setActivity(activity)
                avatar.setPresence(AvatarPresence.AVAILABLE)
                activity_layout.addWidget(avatar)
                self.test_avatars.append(avatar)

        layout.addLayout(activity_layout)

        # Interactive features
        interactive_group = QGroupBox("Interactive Features")
        interactive_layout = QVBoxLayout(interactive_group)

        # Clickable avatar
        click_avatar = FluentAvatar()
        click_avatar.setSize(FluentAvatar.Size.XLARGE)
        click_avatar.setText("CLICK")
        click_avatar.setPresence(AvatarPresence.AVAILABLE)
        click_avatar.setClickable(True)
        click_avatar.clicked.connect(
            lambda: self.show_message("Avatar clicked!"))
        interactive_layout.addWidget(
            click_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.test_avatars.append(click_avatar)

        # Status display
        self.status_label = QLabel("Click the avatar above!")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        interactive_layout.addWidget(self.status_label)

        layout.addWidget(interactive_group)
        parent_layout.addWidget(group)

    def create_group_avatar_demo(self, parent_layout):
        """Create avatar group demonstration section"""
        group = QGroupBox("Avatar Group Features")
        group.setMinimumWidth(400)
        layout = QVBoxLayout(group)

        # Title
        title = QLabel(" Avatar Groups")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Small group
        small_group_label = QLabel("Small Group (3 avatars):")
        layout.addWidget(small_group_label)

        small_group = FluentAvatarGroup()
        small_group.setSize(FluentAvatar.Size.MEDIUM)
        small_group.setMaxVisible(5)

        for i in range(3):
            avatar = FluentAvatar()
            avatar.setText(f"U{i+1}")
            avatar.setPresence(AvatarPresence.AVAILABLE if i %
                               2 else AvatarPresence.AWAY)
            small_group.addAvatar(avatar)

        layout.addWidget(small_group)

        # Large group with overflow
        large_group_label = QLabel("Large Group (8 avatars, max 5 visible):")
        layout.addWidget(large_group_label)

        large_group = FluentAvatarGroup()
        large_group.setSize(FluentAvatar.Size.SMALL)
        large_group.setMaxVisible(5)
        large_group.setOverlap(2)

        presences = list(AvatarPresence)[1:]  # Skip NONE
        for i in range(8):
            avatar = FluentAvatar()
            avatar.setText(f"G{i+1}")
            avatar.setPresence(presences[i % len(presences)])
            large_group.addAvatar(avatar)

        layout.addWidget(large_group)

        # Compact group
        compact_group_label = QLabel("Compact Mode:")
        layout.addWidget(compact_group_label)

        compact_group = FluentAvatarGroup()
        compact_group.setSize(FluentAvatar.Size.TINY)
        compact_group.setMaxVisible(10)
        compact_group.setCompactMode(True)

        for i in range(6):
            avatar = FluentAvatar()
            avatar.setText(f"C{i+1}")
            avatar.setPresence(AvatarPresence.AVAILABLE)
            compact_group.addAvatar(avatar)

        layout.addWidget(compact_group)

        # Dynamic group controls
        controls_group = QGroupBox("Dynamic Controls")
        controls_layout = QVBoxLayout(controls_group)

        # Add/Remove buttons
        button_layout = QHBoxLayout()

        add_btn = QPushButton("Add Avatar")
        add_btn.clicked.connect(lambda: self.add_dynamic_avatar(large_group))
        button_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove Avatar")
        remove_btn.clicked.connect(
            lambda: self.remove_dynamic_avatar(large_group))
        button_layout.addWidget(remove_btn)

        controls_layout.addLayout(button_layout)

        # Animation trigger
        animate_btn = QPushButton("Trigger Entrance Animation")
        animate_btn.clicked.connect(lambda: large_group._show_group_entrance())
        controls_layout.addWidget(animate_btn)

        layout.addWidget(controls_group)
        parent_layout.addWidget(group)

    def create_controls_panel(self, parent_layout):
        """Create controls panel for testing features"""
        group = QGroupBox("Live Controls")
        group.setMinimumWidth(300)
        layout = QVBoxLayout(group)

        # Title
        title = QLabel("Real-time Testing")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Test avatar
        self.control_avatar = FluentAvatar()
        self.control_avatar.setSize(FluentAvatar.Size.XLARGE)
        self.control_avatar.setText("TEST")
        self.control_avatar.setPresence(AvatarPresence.AVAILABLE)
        layout.addWidget(self.control_avatar,
                         alignment=Qt.AlignmentFlag.AlignCenter)

        # Size control
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        size_combo = QComboBox()
        size_combo.addItems([size.name for size in FluentAvatar.Size])
        size_combo.setCurrentText("XLARGE")
        size_combo.currentTextChanged.connect(
            lambda text: self.control_avatar.setSize(FluentAvatar.Size[text])
        )
        size_layout.addWidget(size_combo)
        layout.addLayout(size_layout)

        # Shape control
        shape_layout = QHBoxLayout()
        shape_layout.addWidget(QLabel("Shape:"))
        shape_combo = QComboBox()
        shape_combo.addItems(['circle', 'rounded_square', 'hexagon'])
        shape_combo.currentTextChanged.connect(self.control_avatar.setShape)
        shape_layout.addWidget(shape_combo)
        layout.addLayout(shape_layout)

        # Presence control
        presence_layout = QHBoxLayout()
        presence_layout.addWidget(QLabel("Presence:"))
        presence_combo = QComboBox()
        presence_combo.addItems([p.value for p in AvatarPresence])
        presence_combo.setCurrentText("available")
        presence_combo.currentTextChanged.connect(
            lambda text: self.control_avatar.setPresence(AvatarPresence(text))
        )
        presence_layout.addWidget(presence_combo)
        layout.addLayout(presence_layout)

        # Activity control
        activity_layout = QHBoxLayout()
        activity_layout.addWidget(QLabel("Activity:"))
        activity_combo = QComboBox()
        activity_combo.addItems([a.value for a in AvatarActivity])
        activity_combo.currentTextChanged.connect(
            lambda text: self.control_avatar.setActivity(AvatarActivity(text))
        )
        activity_layout.addWidget(activity_combo)
        layout.addLayout(activity_layout)

        # Animation controls
        animation_group = QGroupBox("Animations")
        animation_layout = QVBoxLayout(animation_group)

        glow_btn = QPushButton("Glow Effect")
        glow_btn.clicked.connect(self.control_avatar.animateGlow)
        animation_layout.addWidget(glow_btn)

        pulse_btn = QPushButton("Pulse Animation")
        pulse_btn.clicked.connect(self.control_avatar.animatePulse)
        animation_layout.addWidget(pulse_btn)

        bounce_btn = QPushButton("Bounce Effect")
        bounce_btn.clicked.connect(self.control_avatar.animateBounce)
        animation_layout.addWidget(bounce_btn)

        layout.addWidget(animation_group)

        # Performance info
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)

        self.perf_label = QLabel("Cache hits: 0\nRender time: 0ms")
        perf_layout.addWidget(self.perf_label)

        # Update performance info periodically
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.update_performance_info)
        self.perf_timer.start(1000)

        layout.addWidget(perf_group)
        parent_layout.addWidget(group)

    def add_dynamic_avatar(self, group):
        """Add a new avatar to the group dynamically"""
        avatar = FluentAvatar()
        avatar.setText(f"N{group.count() + 1}")
        avatar.setPresence(AvatarPresence.AVAILABLE)
        group.addAvatar(avatar)
        self.show_message(f"Added avatar. Total: {group.count()}")

    def remove_dynamic_avatar(self, group):
        """Remove an avatar from the group dynamically"""
        if group.count() > 0:
            group.removeAvatar(group.count() - 1)
            self.show_message(f"Removed avatar. Total: {group.count()}")
        else:
            self.show_message("No avatars to remove!")

    def animate_demo(self):
        """Periodic demo animations"""
        if self.test_avatars:
            # Randomly animate some avatars
            import random
            avatar = random.choice(self.test_avatars)
            animations = [avatar.animateGlow,
                          avatar.animatePulse, avatar.animateBounce]
            random.choice(animations)()

    def update_performance_info(self):
        """Update performance information display"""
        if hasattr(self.control_avatar, '_cache_hits'):
            cache_hits = getattr(self.control_avatar, '_cache_hits', 0)
            render_time = getattr(self.control_avatar, '_last_render_time', 0)
            self.perf_label.setText(
                f"Cache hits: {cache_hits}\nRender time: {render_time:.1f}ms")

    def show_message(self, message):
        """Show a status message"""
        self.status_label.setText(message)
        QTimer.singleShot(2000, lambda: self.status_label.setText(
            "Click the avatar above!"))


class AvatarPerformanceTest(QWidget):
    """Performance testing widget for avatar rendering"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avatar Performance Test")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout(self)

        # Controls
        controls = QHBoxLayout()

        self.count_spinbox = QSpinBox()
        self.count_spinbox.setRange(1, 1000)
        self.count_spinbox.setValue(50)
        controls.addWidget(QLabel("Avatar Count:"))
        controls.addWidget(self.count_spinbox)

        test_btn = QPushButton("Run Performance Test")
        test_btn.clicked.connect(self.run_performance_test)
        controls.addWidget(test_btn)

        layout.addLayout(controls)

        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        # Test container
        self.test_scroll = QScrollArea()
        self.test_widget = QWidget()
        self.test_layout = QGridLayout(self.test_widget)
        self.test_scroll.setWidget(self.test_widget)
        self.test_scroll.setWidgetResizable(True)
        layout.addWidget(self.test_scroll)

    def run_performance_test(self):
        """Run performance test with specified number of avatars"""
        import time

        count = self.count_spinbox.value()
        self.results_text.append(
            f"\n--- Performance Test: {count} avatars ---")

        # Clear previous test
        for i in reversed(range(self.test_layout.count())):
            item = self.test_layout.itemAt(i)
            if item and item.widget():
                child = item.widget()
                child.setParent(None)

        # Create avatars and measure time
        start_time = time.time()

        cols = int(count ** 0.5) + 1
        for i in range(count):
            avatar = FluentAvatar()
            avatar.setSize(FluentAvatar.Size.SMALL)
            avatar.setText(f"{i%100:02d}")
            avatar.setPresence(list(AvatarPresence)[1:][i % 5])

            row, col = divmod(i, cols)
            self.test_layout.addWidget(avatar, row, col)

        creation_time = time.time() - start_time

        # Force render and measure
        QApplication.processEvents()
        render_start = time.time()
        self.test_widget.repaint()
        QApplication.processEvents()
        render_time = time.time() - render_start

        # Display results
        self.results_text.append(f"Creation time: {creation_time*1000:.2f}ms")
        self.results_text.append(f"Render time: {render_time*1000:.2f}ms")
        self.results_text.append(
            f"Average per avatar: {(creation_time/count)*1000:.2f}ms")
        self.results_text.append(
            f"Memory usage: {self.get_memory_usage():.1f}MB")

    def get_memory_usage(self):
        """Get approximate memory usage"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName(" Avatar Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Fluent Widget")

    # Create and show main demo window
    demo_window = AvatarDemoWindow()
    demo_window.show()

    # Optionally show performance test window
    if "--performance" in sys.argv:
        perf_window = AvatarPerformanceTest()
        perf_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
