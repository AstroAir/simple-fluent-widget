"""
Fluent Loading Components Demo
Comprehensive example showcasing all loading indicators and their features
"""

import sys
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QGroupBox,
    QScrollArea, QFrame, QLineEdit, QSpinBox, QSlider,
    QCheckBox, QTextEdit, QSizePolicy, QProgressBar, QTabWidget
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QColor

# Import the loading components
from components.basic.loading import (
    FluentSpinner, FluentDotLoader, FluentProgressRing, 
    FluentLoadingOverlay, FluentPulseLoader
)
from core.theme import theme_manager, ThemeMode


class WorkerThread(QThread):
    """Simulate background work for demonstration"""
    progress_updated = Signal(float)
    finished_work = Signal()

    def __init__(self, duration=5):
        super().__init__()
        self.duration = duration
        self.should_stop = False

    def run(self):
        """Simulate work with progress updates"""
        steps = 100
        for i in range(steps + 1):
            if self.should_stop:
                break
            
            progress = i / steps
            self.progress_updated.emit(progress)
            self.msleep(int(self.duration * 1000 / steps))
        
        if not self.should_stop:
            self.finished_work.emit()

    def stop_work(self):
        """Stop the work"""
        self.should_stop = True


class LoadingDemo(QMainWindow):
    """Main demo window showcasing all loading features"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Loading Components Demo")
        self.setGeometry(100, 100, 1400, 1000)

        # Store overlay reference
        self.current_overlay = None
        self.worker_thread = None

        # Central widget with scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        # Main layout
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Fluent Loading Components Demo")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Theme toggle
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        if theme_manager.get_theme_mode() == ThemeMode.DARK:
            self.theme_combo.setCurrentText("Dark")
        else:
            self.theme_combo.setCurrentText("Light")
        self.theme_combo.currentTextChanged.connect(self._toggle_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        main_layout.addLayout(theme_layout)

        # Create demo sections using tabs
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_spinner_demo(), "Spinners")
        tab_widget.addTab(self._create_dot_loader_demo(), "Dot Loaders")
        tab_widget.addTab(self._create_progress_ring_demo(), "Progress Rings")
        tab_widget.addTab(self._create_pulse_loader_demo(), "Pulse Loaders")
        tab_widget.addTab(self._create_overlay_demo(), "Loading Overlays")
        tab_widget.addTab(self._create_interactive_demo(), "Interactive Demo")
        
        main_layout.addWidget(tab_widget)
        main_layout.addStretch()

    def _create_spinner_demo(self) -> QWidget:
        """Create FluentSpinner demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Basic spinners
        basic_group = QGroupBox("Basic Spinners")
        basic_layout = QGridLayout(basic_group)
        
        # Different sizes
        sizes = [16, 24, 32, 48, 64]
        for i, size in enumerate(sizes):
            label = QLabel(f"{size}px")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            basic_layout.addWidget(label, 0, i)
            
            spinner = FluentSpinner(size=size)
            spinner.start()
            basic_layout.addWidget(spinner, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(basic_group)

        # Different line widths
        width_group = QGroupBox("Different Line Widths")
        width_layout = QGridLayout(width_group)
        
        widths = [1, 2, 3, 4, 6]
        for i, width in enumerate(widths):
            label = QLabel(f"Width: {width}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            width_layout.addWidget(label, 0, i)
            
            spinner = FluentSpinner(size=40, line_width=width)
            spinner.start()
            width_layout.addWidget(spinner, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(width_group)

        # Custom colors
        color_group = QGroupBox("Custom Colors")
        color_layout = QGridLayout(color_group)
        
        colors = [
            ("Default", None),
            ("Red", QColor(255, 0, 0)),
            ("Green", QColor(0, 255, 0)),
            ("Blue", QColor(0, 0, 255)),
            ("Purple", QColor(128, 0, 128))
        ]
        
        for i, (name, color) in enumerate(colors):
            label = QLabel(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            color_layout.addWidget(label, 0, i)
            
            spinner = FluentSpinner(size=36, color=color)
            spinner.start()
            color_layout.addWidget(spinner, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(color_group)

        # Control spinner
        control_group = QGroupBox("Controllable Spinner")
        control_layout = QVBoxLayout(control_group)
        
        self.control_spinner = FluentSpinner(size=48)
        control_layout.addWidget(self.control_spinner, 0, Qt.AlignmentFlag.AlignCenter)
        
        button_layout = QHBoxLayout()
        start_btn = QPushButton("Start")
        start_btn.clicked.connect(self.control_spinner.start)
        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.control_spinner.stop)
        
        button_layout.addWidget(start_btn)
        button_layout.addWidget(stop_btn)
        button_layout.addStretch()
        
        control_layout.addLayout(button_layout)
        layout.addWidget(control_group)

        return widget

    def _create_dot_loader_demo(self) -> QWidget:
        """Create FluentDotLoader demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Different dot counts
        count_group = QGroupBox("Different Dot Counts")
        count_layout = QGridLayout(count_group)
        
        dot_counts = [3, 4, 5, 6, 8]
        for i, count in enumerate(dot_counts):
            label = QLabel(f"{count} dots")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            count_layout.addWidget(label, 0, i)
            
            dot_loader = FluentDotLoader(dot_count=count)
            dot_loader.start()
            count_layout.addWidget(dot_loader, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(count_group)

        # Different dot sizes
        size_group = QGroupBox("Different Dot Sizes")
        size_layout = QGridLayout(size_group)
        
        dot_sizes = [4, 6, 8, 10, 12]
        for i, size in enumerate(dot_sizes):
            label = QLabel(f"{size}px")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            size_layout.addWidget(label, 0, i)
            
            dot_loader = FluentDotLoader(dot_count=4, dot_size=size)
            dot_loader.start()
            size_layout.addWidget(dot_loader, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(size_group)

        # Different spacing
        spacing_group = QGroupBox("Different Spacing")
        spacing_layout = QGridLayout(spacing_group)
        
        spacings = [2, 4, 6, 8, 12]
        for i, spacing in enumerate(spacings):
            label = QLabel(f"Spacing: {spacing}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spacing_layout.addWidget(label, 0, i)
            
            dot_loader = FluentDotLoader(dot_count=4, spacing=spacing)
            dot_loader.start()
            spacing_layout.addWidget(dot_loader, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(spacing_group)

        # Custom colors
        dot_color_group = QGroupBox("Custom Colors")
        dot_color_layout = QGridLayout(dot_color_group)
        
        dot_colors = [
            ("Default", None),
            ("Orange", QColor(255, 165, 0)),
            ("Cyan", QColor(0, 255, 255)),
            ("Pink", QColor(255, 192, 203)),
            ("Yellow", QColor(255, 255, 0))
        ]
        
        for i, (name, color) in enumerate(dot_colors):
            label = QLabel(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot_color_layout.addWidget(label, 0, i)
            
            dot_loader = FluentDotLoader(dot_count=5, color=color)
            dot_loader.start()
            dot_color_layout.addWidget(dot_loader, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(dot_color_group)

        # Control dot loader
        dot_control_group = QGroupBox("Controllable Dot Loader")
        dot_control_layout = QVBoxLayout(dot_control_group)
        
        self.control_dot_loader = FluentDotLoader(dot_count=6)
        dot_control_layout.addWidget(self.control_dot_loader, 0, Qt.AlignmentFlag.AlignCenter)
        
        dot_button_layout = QHBoxLayout()
        start_dots_btn = QPushButton("Start")
        start_dots_btn.clicked.connect(self.control_dot_loader.start)
        stop_dots_btn = QPushButton("Stop")
        stop_dots_btn.clicked.connect(self.control_dot_loader.stop)
        
        dot_button_layout.addWidget(start_dots_btn)
        dot_button_layout.addWidget(stop_dots_btn)
        dot_button_layout.addStretch()
        
        dot_control_layout.addLayout(dot_button_layout)
        layout.addWidget(dot_control_group)

        return widget

    def _create_progress_ring_demo(self) -> QWidget:
        """Create FluentProgressRing demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Indeterminate rings
        indeterminate_group = QGroupBox("Indeterminate Progress Rings")
        indeterminate_layout = QGridLayout(indeterminate_group)
        
        ring_sizes = [32, 40, 48, 56, 64]
        for i, size in enumerate(ring_sizes):
            label = QLabel(f"{size}px")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            indeterminate_layout.addWidget(label, 0, i)
            
            progress_ring = FluentProgressRing(size=size, indeterminate=True)
            indeterminate_layout.addWidget(progress_ring, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(indeterminate_group)

        # Determinate rings
        determinate_group = QGroupBox("Determinate Progress Rings")
        determinate_layout = QGridLayout(determinate_group)
        
        progress_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        for i, value in enumerate(progress_values):
            label = QLabel(f"{int(value * 100)}%")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            determinate_layout.addWidget(label, 0, i)
            
            progress_ring = FluentProgressRing(size=48, indeterminate=False, value=value)
            determinate_layout.addWidget(progress_ring, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(determinate_group)

        # Different line widths
        ring_width_group = QGroupBox("Different Line Widths")
        ring_width_layout = QGridLayout(ring_width_group)
        
        line_widths = [2, 3, 4, 5, 6]
        for i, width in enumerate(line_widths):
            label = QLabel(f"Width: {width}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ring_width_layout.addWidget(label, 0, i)
            
            progress_ring = FluentProgressRing(size=48, line_width=width, value=0.6)
            ring_width_layout.addWidget(progress_ring, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(ring_width_group)

        # Interactive progress ring
        interactive_group = QGroupBox("Interactive Progress Ring")
        interactive_layout = QVBoxLayout(interactive_group)
        
        ring_container = QHBoxLayout()
        
        self.interactive_ring = FluentProgressRing(size=80, indeterminate=False, value=0.3)
        ring_container.addWidget(self.interactive_ring, 0, Qt.AlignmentFlag.AlignCenter)
        
        controls_layout = QVBoxLayout()
        
        # Progress slider
        progress_slider_layout = QHBoxLayout()
        progress_slider_layout.addWidget(QLabel("Progress:"))
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(30)
        self.progress_slider.valueChanged.connect(self._update_progress_ring)
        progress_slider_layout.addWidget(self.progress_slider)
        
        self.progress_label = QLabel("30%")
        progress_slider_layout.addWidget(self.progress_label)
        
        controls_layout.addLayout(progress_slider_layout)
        
        # Mode toggle
        mode_layout = QHBoxLayout()
        self.indeterminate_cb = QCheckBox("Indeterminate Mode")
        self.indeterminate_cb.toggled.connect(self._toggle_ring_mode)
        mode_layout.addWidget(self.indeterminate_cb)
        mode_layout.addStretch()
        
        controls_layout.addLayout(mode_layout)
        
        # Animation controls
        anim_layout = QHBoxLayout()
        animate_to_50_btn = QPushButton("Animate to 50%")
        animate_to_50_btn.clicked.connect(lambda: self.interactive_ring.setValue(0.5, animate=True))
        
        animate_to_100_btn = QPushButton("Animate to 100%")
        animate_to_100_btn.clicked.connect(lambda: self.interactive_ring.setValue(1.0, animate=True))
        
        reset_btn = QPushButton("Reset to 0%")
        reset_btn.clicked.connect(lambda: self.interactive_ring.setValue(0.0, animate=True))
        
        anim_layout.addWidget(animate_to_50_btn)
        anim_layout.addWidget(animate_to_100_btn)
        anim_layout.addWidget(reset_btn)
        anim_layout.addStretch()
        
        controls_layout.addLayout(anim_layout)
        ring_container.addLayout(controls_layout)
        
        interactive_layout.addLayout(ring_container)
        layout.addWidget(interactive_group)

        return widget

    def _create_pulse_loader_demo(self) -> QWidget:
        """Create FluentPulseLoader demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Basic pulse loaders
        basic_pulse_group = QGroupBox("Basic Pulse Loaders")
        basic_pulse_layout = QGridLayout(basic_pulse_group)
        
        pulse_sizes = [20, 30, 40, 50, 60]
        for i, size in enumerate(pulse_sizes):
            label = QLabel(f"{size}px")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            basic_pulse_layout.addWidget(label, 0, i)
            
            pulse_loader = FluentPulseLoader(size=size)
            pulse_loader.start()
            basic_pulse_layout.addWidget(pulse_loader, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(basic_pulse_group)

        # Custom colors
        pulse_color_group = QGroupBox("Custom Colors")
        pulse_color_layout = QGridLayout(pulse_color_group)
        
        pulse_colors = [
            ("Default", None),
            ("Red", QColor(255, 100, 100)),
            ("Green", QColor(100, 255, 100)),
            ("Blue", QColor(100, 100, 255)),
            ("Gold", QColor(255, 215, 0))
        ]
        
        for i, (name, color) in enumerate(pulse_colors):
            label = QLabel(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pulse_color_layout.addWidget(label, 0, i)
            
            pulse_loader = FluentPulseLoader(size=40, color=color)
            pulse_loader.start()
            pulse_color_layout.addWidget(pulse_loader, 1, i, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(pulse_color_group)

        # Control pulse loader
        pulse_control_group = QGroupBox("Controllable Pulse Loader")
        pulse_control_layout = QVBoxLayout(pulse_control_group)
        
        self.control_pulse_loader = FluentPulseLoader(size=60)
        pulse_control_layout.addWidget(self.control_pulse_loader, 0, Qt.AlignmentFlag.AlignCenter)
        
        pulse_button_layout = QHBoxLayout()
        start_pulse_btn = QPushButton("Start")
        start_pulse_btn.clicked.connect(self.control_pulse_loader.start)
        stop_pulse_btn = QPushButton("Stop")
        stop_pulse_btn.clicked.connect(self.control_pulse_loader.stop)
        
        pulse_button_layout.addWidget(start_pulse_btn)
        pulse_button_layout.addWidget(stop_pulse_btn)
        pulse_button_layout.addStretch()
        
        pulse_control_layout.addLayout(pulse_button_layout)
        layout.addWidget(pulse_control_group)

        # Multiple pulse loaders
        multiple_group = QGroupBox("Multiple Pulse Loaders")
        multiple_layout = QHBoxLayout(multiple_group)
        
        for i in range(5):
            pulse = FluentPulseLoader(size=35)
            pulse.start()
            multiple_layout.addWidget(pulse, 0, Qt.AlignmentFlag.AlignCenter)
        
        multiple_layout.addStretch()
        layout.addWidget(multiple_group)

        return widget

    def _create_overlay_demo(self) -> QWidget:
        """Create FluentLoadingOverlay demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Basic overlay demonstration
        overlay_group = QGroupBox("Loading Overlay Demonstration")
        overlay_layout = QVBoxLayout(overlay_group)
        
        # Demo content area
        self.demo_content_area = QFrame()
        self.demo_content_area.setMinimumHeight(200)
        self.demo_content_area.setStyleSheet("""
            QFrame {
                border: 2px dashed gray;
                border-radius: 8px;
                background-color: rgba(100, 100, 100, 0.1);
            }
        """)
        
        content_layout = QVBoxLayout(self.demo_content_area)
        content_layout.addWidget(QLabel("Demo Content Area", alignment=Qt.AlignmentFlag.AlignCenter))
        content_layout.addWidget(QLabel("Click buttons below to show loading overlay", 
                                       alignment=Qt.AlignmentFlag.AlignCenter))
        
        overlay_layout.addWidget(self.demo_content_area)
        
        # Overlay control buttons
        overlay_controls = QHBoxLayout()
        
        show_basic_overlay_btn = QPushButton("Show Basic Overlay")
        show_basic_overlay_btn.clicked.connect(self._show_basic_overlay)
        
        show_custom_overlay_btn = QPushButton("Show Custom Text Overlay")
        show_custom_overlay_btn.clicked.connect(self._show_custom_overlay)
        
        show_large_overlay_btn = QPushButton("Show Large Spinner Overlay")
        show_large_overlay_btn.clicked.connect(self._show_large_overlay)
        
        hide_overlay_btn = QPushButton("Hide Overlay")
        hide_overlay_btn.clicked.connect(self._hide_overlay)
        
        overlay_controls.addWidget(show_basic_overlay_btn)
        overlay_controls.addWidget(show_custom_overlay_btn)
        overlay_controls.addWidget(show_large_overlay_btn)
        overlay_controls.addWidget(hide_overlay_btn)
        overlay_controls.addStretch()
        
        overlay_layout.addLayout(overlay_controls)
        layout.addWidget(overlay_group)

        # Simulated work demonstration
        work_group = QGroupBox("Simulated Work with Progress")
        work_layout = QVBoxLayout(work_group)
        
        work_info = QLabel("Simulate background work with progress updates:")
        work_layout.addWidget(work_info)
        
        # Progress display
        self.work_progress_bar = QProgressBar()
        self.work_progress_bar.setRange(0, 100)
        self.work_progress_bar.setValue(0)
        work_layout.addWidget(self.work_progress_bar)
        
        # Work control buttons
        work_controls = QHBoxLayout()
        
        start_work_btn = QPushButton("Start Work (5s)")
        start_work_btn.clicked.connect(self._start_simulated_work)
        
        start_long_work_btn = QPushButton("Start Long Work (10s)")
        start_long_work_btn.clicked.connect(self._start_long_work)
        
        stop_work_btn = QPushButton("Stop Work")
        stop_work_btn.clicked.connect(self._stop_work)
        
        self.work_status_label = QLabel("Ready to start work")
        
        work_controls.addWidget(start_work_btn)
        work_controls.addWidget(start_long_work_btn)
        work_controls.addWidget(stop_work_btn)
        work_controls.addWidget(self.work_status_label)
        work_controls.addStretch()
        
        work_layout.addLayout(work_controls)
        layout.addWidget(work_group)

        return widget

    def _create_interactive_demo(self) -> QWidget:
        """Create interactive demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # All loaders showcase
        showcase_group = QGroupBox("All Loading Components Showcase")
        showcase_layout = QGridLayout(showcase_group)
        
        # Create and store all demo loaders
        self.demo_loaders = {}
        
        # Spinner
        spinner_container = QVBoxLayout()
        spinner_container.addWidget(QLabel("Spinner", alignment=Qt.AlignmentFlag.AlignCenter))
        self.demo_loaders['spinner'] = FluentSpinner(size=40)
        spinner_container.addWidget(self.demo_loaders['spinner'], 0, Qt.AlignmentFlag.AlignCenter)
        showcase_layout.addLayout(spinner_container, 0, 0)
        
        # Dot Loader
        dot_container = QVBoxLayout()
        dot_container.addWidget(QLabel("Dot Loader", alignment=Qt.AlignmentFlag.AlignCenter))
        self.demo_loaders['dots'] = FluentDotLoader(dot_count=5)
        dot_container.addWidget(self.demo_loaders['dots'], 0, Qt.AlignmentFlag.AlignCenter)
        showcase_layout.addLayout(dot_container, 0, 1)
        
        # Progress Ring
        ring_container = QVBoxLayout()
        ring_container.addWidget(QLabel("Progress Ring", alignment=Qt.AlignmentFlag.AlignCenter))
        self.demo_loaders['ring'] = FluentProgressRing(size=40, indeterminate=True)
        ring_container.addWidget(self.demo_loaders['ring'], 0, Qt.AlignmentFlag.AlignCenter)
        showcase_layout.addLayout(ring_container, 0, 2)
        
        # Pulse Loader
        pulse_container = QVBoxLayout()
        pulse_container.addWidget(QLabel("Pulse Loader", alignment=Qt.AlignmentFlag.AlignCenter))
        self.demo_loaders['pulse'] = FluentPulseLoader(size=40)
        pulse_container.addWidget(self.demo_loaders['pulse'], 0, Qt.AlignmentFlag.AlignCenter)
        showcase_layout.addLayout(pulse_container, 0, 3)
        
        layout.addWidget(showcase_group)

        # Global controls
        global_controls_group = QGroupBox("Global Controls")
        global_controls_layout = QHBoxLayout(global_controls_group)
        
        start_all_btn = QPushButton("Start All")
        start_all_btn.clicked.connect(self._start_all_loaders)
        
        stop_all_btn = QPushButton("Stop All")
        stop_all_btn.clicked.connect(self._stop_all_loaders)
        
        global_controls_layout.addWidget(start_all_btn)
        global_controls_layout.addWidget(stop_all_btn)
        global_controls_layout.addStretch()
        
        layout.addWidget(global_controls_group)

        # Customization controls
        custom_group = QGroupBox("Customization")
        custom_layout = QGridLayout(custom_group)
        
        # Size control
        custom_layout.addWidget(QLabel("Size:"), 0, 0)
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(20, 80)
        self.size_slider.setValue(40)
        self.size_slider.valueChanged.connect(self._update_loader_sizes)
        custom_layout.addWidget(self.size_slider, 0, 1)
        self.size_label = QLabel("40px")
        custom_layout.addWidget(self.size_label, 0, 2)
        
        # Color control
        custom_layout.addWidget(QLabel("Color:"), 1, 0)
        color_layout = QHBoxLayout()
        
        self.use_theme_color = QCheckBox("Use Theme Color")
        self.use_theme_color.setChecked(True)
        self.use_theme_color.toggled.connect(self._update_loader_colors)
        color_layout.addWidget(self.use_theme_color)
        
        color_buttons = [
            ("Red", QColor(255, 0, 0)),
            ("Green", QColor(0, 255, 0)),
            ("Blue", QColor(0, 0, 255)),
            ("Purple", QColor(128, 0, 128))
        ]
        
        for name, color in color_buttons:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, c=color: self._set_loader_color(c))
            color_layout.addWidget(btn)
        
        custom_layout.addLayout(color_layout, 1, 1, 1, 2)
        
        layout.addWidget(custom_group)

        # Performance test
        perf_group = QGroupBox("Performance Test")
        perf_layout = QVBoxLayout(perf_group)
        
        create_many_btn = QPushButton("Create 20 Loading Components")
        create_many_btn.clicked.connect(self._create_many_loaders)
        
        clear_many_btn = QPushButton("Clear Performance Test")
        clear_many_btn.clicked.connect(self._clear_many_loaders)
        
        perf_controls = QHBoxLayout()
        perf_controls.addWidget(create_many_btn)
        perf_controls.addWidget(clear_many_btn)
        perf_controls.addStretch()
        
        perf_layout.addLayout(perf_controls)
        
        # Container for many loaders
        self.many_loaders_container = QFrame()
        self.many_loaders_layout = QGridLayout(self.many_loaders_container)
        perf_layout.addWidget(self.many_loaders_container)
        
        layout.addWidget(perf_group)

        return widget

    def _update_progress_ring(self, value: int):
        """Update progress ring value"""
        progress = value / 100.0
        self.interactive_ring.setValue(progress, animate=False)
        self.progress_label.setText(f"{value}%")

    def _toggle_ring_mode(self, indeterminate: bool):
        """Toggle progress ring mode"""
        self.interactive_ring.setIndeterminate(indeterminate)
        self.progress_slider.setEnabled(not indeterminate)

    def _show_basic_overlay(self):
        """Show basic loading overlay"""
        if self.current_overlay:
            self.current_overlay.hide()
        
        self.current_overlay = FluentLoadingOverlay(self.demo_content_area, "Loading...")
        self.current_overlay.show()

    def _show_custom_overlay(self):
        """Show custom text overlay"""
        if self.current_overlay:
            self.current_overlay.hide()
        
        self.current_overlay = FluentLoadingOverlay(self.demo_content_area, "Processing your request...")
        self.current_overlay.show()

    def _show_large_overlay(self):
        """Show large spinner overlay"""
        if self.current_overlay:
            self.current_overlay.hide()
        
        self.current_overlay = FluentLoadingOverlay(self.demo_content_area, "Please wait...", spinner_size=64)
        self.current_overlay.show()

    def _hide_overlay(self):
        """Hide current overlay"""
        if self.current_overlay:
            self.current_overlay.hide()
            self.current_overlay = None

    def _start_simulated_work(self):
        """Start simulated work"""
        self._start_work_with_duration(5)

    def _start_long_work(self):
        """Start long simulated work"""
        self._start_work_with_duration(10)

    def _start_work_with_duration(self, duration: int):
        """Start work with specified duration"""
        if self.worker_thread and self.worker_thread.isRunning():
            return
        
        self.worker_thread = WorkerThread(duration)
        self.worker_thread.progress_updated.connect(self._update_work_progress)
        self.worker_thread.finished_work.connect(self._work_finished)
        self.worker_thread.start()
        
        self.work_status_label.setText(f"Working... ({duration}s)")
        self.work_progress_bar.setValue(0)
        
        # Show overlay during work
        if self.current_overlay:
            self.current_overlay.hide()
        self.current_overlay = FluentLoadingOverlay(self.demo_content_area, f"Working for {duration} seconds...")
        self.current_overlay.show()

    def _stop_work(self):
        """Stop current work"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop_work()
            self.worker_thread.wait()
        
        self.work_status_label.setText("Work stopped")
        self._hide_overlay()

    def _update_work_progress(self, progress: float):
        """Update work progress"""
        self.work_progress_bar.setValue(int(progress * 100))

    def _work_finished(self):
        """Handle work completion"""
        self.work_status_label.setText("Work completed!")
        self._hide_overlay()

    def _start_all_loaders(self):
        """Start all demo loaders"""
        for loader in self.demo_loaders.values():
            loader.start()

    def _stop_all_loaders(self):
        """Stop all demo loaders"""
        for loader in self.demo_loaders.values():
            loader.stop()

    def _update_loader_sizes(self, size: int):
        """Update loader sizes"""
        self.size_label.setText(f"{size}px")
        
        if 'spinner' in self.demo_loaders:
            self.demo_loaders['spinner'].setSize(size)
        
        # Note: Other loaders would need size update methods
        # This is a simplified demonstration

    def _update_loader_colors(self, use_theme: bool):
        """Update loader colors"""
        if use_theme:
            for loader in self.demo_loaders.values():
                loader.setColor(None)

    def _set_loader_color(self, color: QColor):
        """Set specific color for loaders"""
        self.use_theme_color.setChecked(False)
        for loader in self.demo_loaders.values():
            loader.setColor(color)

    def _create_many_loaders(self):
        """Create many loaders for performance testing"""
        self._clear_many_loaders()
        
        loader_types = [
            lambda: FluentSpinner(size=24),
            lambda: FluentDotLoader(dot_count=3, dot_size=6),
            lambda: FluentProgressRing(size=24, indeterminate=True),
            lambda: FluentPulseLoader(size=24)
        ]
        
        for i in range(20):
            loader_type = loader_types[i % len(loader_types)]
            loader = loader_type()
            loader.start()
            
            row = i // 5
            col = i % 5
            self.many_loaders_layout.addWidget(loader, row, col, Qt.AlignmentFlag.AlignCenter)

    def _clear_many_loaders(self):
        """Clear performance test loaders"""
        while self.many_loaders_layout.count():
            child = self.many_loaders_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _toggle_theme(self, theme_name: str):
        """Toggle between light and dark themes"""
        if theme_name == "Dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)

    def closeEvent(self, event):
        """Clean up on close"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop_work()
            self.worker_thread.wait()
        
        if self.current_overlay:
            self.current_overlay.hide()
        
        event.accept()


def main():
    """Run the loading demo application"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show demo window
    demo = LoadingDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()