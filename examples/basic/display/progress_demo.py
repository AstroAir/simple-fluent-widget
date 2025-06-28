"""
Fluent Progress Components Demo
Comprehensive example showcasing all progress and slider components
"""

import sys
# import time # Unused in this file
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QGroupBox,
    QScrollArea, QLineEdit, QSpinBox, QSlider, # QFrame removed (unused)
    QCheckBox, QTextEdit, QTabWidget # QSizePolicy, QFormLayout removed (unused)
    # QButtonGroup, QRadioButton, QFileDialog, QMessageBox, QDoubleSpinBox removed (unused)
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal # QPropertyAnimation, QEasingCurve removed (unused by demo.py)
from PySide6.QtGui import QFont # QColor removed (unused by demo.py)

# Import the progress components
from components.basic.progress import (
    FluentProgressBar, FluentProgressRing, FluentSlider, 
    FluentRangeSlider, FluentProgressIndicator
)
from core.theme import theme_manager, ThemeMode
# from core.animation import FluentAnimation # Unused by demo.py


class WorkerThread(QThread):
    """Simulate background work with progress updates"""
    progress_updated = Signal(int)
    stage_changed = Signal(str)
    finished_work = Signal()

    def __init__(self, duration=5, stages=None):
        super().__init__()
        self.duration = duration
        self.stages = stages or ["Initializing", "Processing", "Finalizing"]
        self.should_stop = False

    def run(self):
        """Simulate work with progress updates"""
        total_steps = 100
        if not self.stages: # Avoid division by zero if stages is empty
            self.finished_work.emit()
            return
            
        stage_steps = total_steps // len(self.stages)
        
        for stage_idx, stage in enumerate(self.stages):
            if self.should_stop:
                break
                
            self.stage_changed.emit(stage)
            
            for step in range(stage_steps):
                if self.should_stop:
                    break
                
                overall_progress = (stage_idx * stage_steps + step)
                self.progress_updated.emit(overall_progress)
                self.msleep(int(self.duration * 1000 / total_steps))
        
        if not self.should_stop:
            self.progress_updated.emit(100)
            self.finished_work.emit()

    def stop_work(self):
        """Stop the work"""
        self.should_stop = True


class FileDownloadSimulator(QThread):
    """Simulate file download with variable speed"""
    progress_updated = Signal(int)
    speed_changed = Signal(str)
    finished_download = Signal()

    def __init__(self, file_size_mb=100):
        super().__init__()
        self.file_size_mb = file_size_mb
        self.should_stop = False

    def run(self):
        """Simulate download with variable speed"""
        downloaded = 0
        total_size = self.file_size_mb * 1024 * 1024  # Convert to bytes
        
        while downloaded < total_size and not self.should_stop:
            # Simulate variable download speed (1-10 MB/s)
            speed_mbps = random.uniform(1, 10)
            speed_bps = speed_mbps * 1024 * 1024
            
            chunk_size = int(speed_bps * 0.1)  # 100ms chunks
            downloaded += chunk_size
            
            progress = min(100, int(downloaded / total_size * 100))
            self.progress_updated.emit(progress)
            self.speed_changed.emit(f"{speed_mbps:.1f} MB/s")
            
            self.msleep(100)
        
        if not self.should_stop:
            self.progress_updated.emit(100) # Ensure 100% on completion
            self.finished_download.emit()

    def stop_download(self):
        """Stop the download"""
        self.should_stop = True


class ProgressDemo(QMainWindow):
    """Main demo window showcasing all progress components"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Progress Components Demo")
        self.setGeometry(100, 100, 1400, 1000)

        # Store worker references
        self.worker_threads = [] # Consider managing these more actively if needed
        self.timers = []

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
        title = QLabel("Fluent Progress Components Demo")
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
        tab_widget.addTab(self._create_progress_bars_demo(), "Progress Bars")
        tab_widget.addTab(self._create_progress_rings_demo(), "Progress Rings")
        tab_widget.addTab(self._create_sliders_demo(), "Sliders")
        tab_widget.addTab(self._create_range_sliders_demo(), "Range Sliders")
        tab_widget.addTab(self._create_indicators_demo(), "Progress Indicators")
        tab_widget.addTab(self._create_real_world_demo(), "Real-World Examples")
        tab_widget.addTab(self._create_interactive_demo(), "Interactive Demo")
        
        main_layout.addWidget(tab_widget)
        main_layout.addStretch()

    def _create_progress_bars_demo(self) -> QWidget:
        """Create FluentProgressBar demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Basic progress bars
        basic_group = QGroupBox("Basic Progress Bars")
        basic_layout = QVBoxLayout(basic_group)
        
        # Different states
        states_layout = QGridLayout()
        
        # Static progress bars
        progress_values = [0, 25, 50, 75, 100]
        for i, value in enumerate(progress_values):
            label = QLabel(f"{value}% Progress")
            states_layout.addWidget(label, 0, i)
            
            progress_bar = FluentProgressBar()
            progress_bar.setValue(value)
            states_layout.addWidget(progress_bar, 1, i)
        
        basic_layout.addLayout(states_layout)
        layout.addWidget(basic_group)

        # Indeterminate progress bars
        indeterminate_group = QGroupBox("Indeterminate Progress Bars")
        indeterminate_layout = QVBoxLayout(indeterminate_group)
        
        indeterminate_info = QLabel("Indeterminate progress bars for unknown duration tasks")
        indeterminate_layout.addWidget(indeterminate_info)
        
        # Multiple indeterminate bars
        indeterminate_bars_layout = QVBoxLayout()
        
        self.indeterminate_bars = []
        for i in range(3):
            bar_layout = QHBoxLayout()
            
            label = QLabel(f"Loading Task {i+1}...")
            bar_layout.addWidget(label)
            
            progress_bar = FluentProgressBar()
            progress_bar.set_indeterminate(True) # Start as indeterminate for demo
            bar_layout.addWidget(progress_bar)
            
            self.indeterminate_bars.append(progress_bar)
            indeterminate_bars_layout.addLayout(bar_layout)
        
        indeterminate_layout.addLayout(indeterminate_bars_layout)
        
        # Control buttons for indeterminate bars
        indeterminate_controls = QHBoxLayout()
        
        start_all_btn = QPushButton("Start All")
        start_all_btn.clicked.connect(self._start_all_indeterminate)
        
        stop_all_btn = QPushButton("Stop All")
        stop_all_btn.clicked.connect(self._stop_all_indeterminate)
        
        toggle_btn = QPushButton("Toggle")
        toggle_btn.clicked.connect(self._toggle_indeterminate)
        
        indeterminate_controls.addWidget(start_all_btn)
        indeterminate_controls.addWidget(stop_all_btn)
        indeterminate_controls.addWidget(toggle_btn)
        indeterminate_controls.addStretch()
        
        indeterminate_layout.addLayout(indeterminate_controls)
        layout.addWidget(indeterminate_group)

        # Animated progress bars
        animated_group = QGroupBox("Animated Progress Updates")
        animated_layout = QVBoxLayout(animated_group)
        
        # Smooth animation progress bar
        animated_layout.addWidget(QLabel("Smooth Animation Progress:"))
        self.animated_progress = FluentProgressBar()
        self.animated_progress.setValue(0)
        animated_layout.addWidget(self.animated_progress)
        
        # Animation controls
        animation_controls = QHBoxLayout()
        
        self.target_value_spinbox = QSpinBox()
        self.target_value_spinbox.setRange(0, 100)
        self.target_value_spinbox.setValue(75)
        
        animate_to_btn = QPushButton("Animate To")
        animate_to_btn.clicked.connect(self._animate_to_value)
        
        random_animate_btn = QPushButton("Random Animation")
        random_animate_btn.clicked.connect(self._random_animation)
        
        reset_btn = QPushButton("Reset to 0")
        reset_btn.clicked.connect(lambda: self.animated_progress.set_value_animated(0))
        
        animation_controls.addWidget(QLabel("Target Value:"))
        animation_controls.addWidget(self.target_value_spinbox)
        animation_controls.addWidget(animate_to_btn)
        animation_controls.addWidget(random_animate_btn)
        animation_controls.addWidget(reset_btn)
        animation_controls.addStretch()
        
        animated_layout.addLayout(animation_controls)
        layout.addWidget(animated_group)

        # Auto-updating progress bars
        auto_group = QGroupBox("Auto-Updating Progress Bars")
        auto_layout = QVBoxLayout(auto_group)
        
        # Slow auto update
        auto_layout.addWidget(QLabel("Slow Auto Update (2s cycle):"))
        self.slow_auto_progress = FluentProgressBar()
        auto_layout.addWidget(self.slow_auto_progress)
        
        # Fast auto update
        auto_layout.addWidget(QLabel("Fast Auto Update (0.5s cycle):"))
        self.fast_auto_progress = FluentProgressBar()
        auto_layout.addWidget(self.fast_auto_progress)
        
        # Auto update controls
        auto_controls = QHBoxLayout()
        
        start_auto_btn = QPushButton("Start Auto Updates")
        start_auto_btn.clicked.connect(self._start_auto_updates)
        
        stop_auto_btn = QPushButton("Stop Auto Updates")
        stop_auto_btn.clicked.connect(self._stop_auto_updates)
        
        auto_controls.addWidget(start_auto_btn)
        auto_controls.addWidget(stop_auto_btn)
        auto_controls.addStretch()
        
        auto_layout.addLayout(auto_controls)
        layout.addWidget(auto_group)

        return widget

    def _create_progress_rings_demo(self) -> QWidget:
        """Create FluentProgressRing demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Basic progress rings
        basic_rings_group = QGroupBox("Basic Progress Rings")
        basic_rings_layout = QVBoxLayout(basic_rings_group)
        
        # Static rings
        rings_grid = QGridLayout()
        
        ring_values = [0, 25, 50, 75, 100]
        self.static_rings = []
        
        for i, value in enumerate(ring_values):
            ring_layout = QVBoxLayout()
            
            label = QLabel(f"{value}%")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ring_layout.addWidget(label)
            
            progress_ring = FluentProgressRing()
            progress_ring.set_value(value)
            ring_layout.addWidget(progress_ring, 0, Qt.AlignmentFlag.AlignCenter)
            
            self.static_rings.append(progress_ring)
            
            ring_widget = QWidget()
            ring_widget.setLayout(ring_layout)
            rings_grid.addWidget(ring_widget, 0, i)
        
        basic_rings_layout.addLayout(rings_grid)
        layout.addWidget(basic_rings_group)

        # Indeterminate rings
        indeterminate_rings_group = QGroupBox("Indeterminate Progress Rings")
        indeterminate_rings_layout = QVBoxLayout(indeterminate_rings_group)
        
        indeterminate_rings_info = QLabel("Spinning rings for unknown duration tasks")
        indeterminate_rings_layout.addWidget(indeterminate_rings_info)
        
        # Multiple indeterminate rings
        rings_container = QHBoxLayout()
        
        self.indeterminate_rings = []
        ring_labels = ["Loading", "Processing", "Syncing", "Uploading"]
        
        for label_text in ring_labels:
            ring_layout = QVBoxLayout()
            
            ring = FluentProgressRing()
            ring.set_indeterminate(True) # Start as indeterminate
            self.indeterminate_rings.append(ring)
            
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            ring_layout.addWidget(ring, 0, Qt.AlignmentFlag.AlignCenter)
            ring_layout.addWidget(label)
            
            ring_widget = QWidget()
            ring_widget.setLayout(ring_layout)
            rings_container.addWidget(ring_widget)
        
        rings_container.addStretch()
        indeterminate_rings_layout.addLayout(rings_container)
        
        # Indeterminate ring controls
        ring_controls = QHBoxLayout()
        
        start_rings_btn = QPushButton("Start All Rings")
        start_rings_btn.clicked.connect(self._start_all_rings)
        
        stop_rings_btn = QPushButton("Stop All Rings")
        stop_rings_btn.clicked.connect(self._stop_all_rings)
        
        ring_controls.addWidget(start_rings_btn)
        ring_controls.addWidget(stop_rings_btn)
        ring_controls.addStretch()
        
        indeterminate_rings_layout.addLayout(ring_controls)
        layout.addWidget(indeterminate_rings_group)

        # Interactive ring
        interactive_ring_group = QGroupBox("Interactive Progress Ring")
        interactive_ring_layout = QVBoxLayout(interactive_ring_group)
        
        ring_container = QHBoxLayout()
        
        # Large interactive ring
        self.interactive_ring = FluentProgressRing()
        self.interactive_ring.setFixedSize(80, 80)
        self.interactive_ring.set_value(50)
        ring_container.addWidget(self.interactive_ring, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Ring controls
        ring_controls_layout = QVBoxLayout()
        
        # Value control
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("Value:"))
        
        self.ring_value_slider = QSlider(Qt.Orientation.Horizontal)
        self.ring_value_slider.setRange(0, 100)
        self.ring_value_slider.setValue(50)
        self.ring_value_slider.valueChanged.connect(self._update_ring_value)
        value_layout.addWidget(self.ring_value_slider)
        
        self.ring_value_label = QLabel("50")
        value_layout.addWidget(self.ring_value_label)
        
        ring_controls_layout.addLayout(value_layout)
        
        # Maximum control
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("Maximum:"))
        
        self.ring_max_spinbox = QSpinBox()
        self.ring_max_spinbox.setRange(1, 1000)
        self.ring_max_spinbox.setValue(100)
        self.ring_max_spinbox.valueChanged.connect(self._update_ring_maximum)
        max_layout.addWidget(self.ring_max_spinbox)
        
        ring_controls_layout.addLayout(max_layout)
        
        # Mode control
        mode_layout = QHBoxLayout()
        self.ring_indeterminate_cb = QCheckBox("Indeterminate Mode")
        self.ring_indeterminate_cb.toggled.connect(self._toggle_ring_mode)
        mode_layout.addWidget(self.ring_indeterminate_cb)
        
        ring_controls_layout.addLayout(mode_layout)
        
        # Animation controls
        anim_layout = QHBoxLayout()
        
        animate_to_25_btn = QPushButton("25%")
        animate_to_25_btn.clicked.connect(lambda: self._animate_ring_to(25))
        
        animate_to_75_btn = QPushButton("75%")
        animate_to_75_btn.clicked.connect(lambda: self._animate_ring_to(75))
        
        animate_to_100_btn = QPushButton("100%")
        animate_to_100_btn.clicked.connect(lambda: self._animate_ring_to(100))
        
        anim_layout.addWidget(animate_to_25_btn)
        anim_layout.addWidget(animate_to_75_btn)
        anim_layout.addWidget(animate_to_100_btn)
        
        ring_controls_layout.addLayout(anim_layout)
        ring_container.addLayout(ring_controls_layout)
        
        interactive_ring_layout.addLayout(ring_container)
        layout.addWidget(interactive_ring_group)

        return widget
    
    def _create_sliders_demo(self) -> QWidget:
        """Create FluentSlider demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Horizontal sliders
        horizontal_group = QGroupBox("Horizontal Sliders")
        horizontal_layout = QVBoxLayout(horizontal_group)
        
        # Basic horizontal slider
        basic_h_layout = QHBoxLayout()
        basic_h_layout.addWidget(QLabel("Basic Horizontal:"))
        
        self.basic_h_slider = FluentSlider(Qt.Orientation.Horizontal)
        self.basic_h_slider.setRange(0, 100)
        self.basic_h_slider.setValue(50)
        basic_h_layout.addWidget(self.basic_h_slider)
        
        self.basic_h_value_label = QLabel("50")
        self.basic_h_slider.valueChanged.connect(lambda v: self.basic_h_value_label.setText(str(v)))
        basic_h_layout.addWidget(self.basic_h_value_label)
        
        horizontal_layout.addLayout(basic_h_layout)
        
        # Volume-style slider
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume Control:"))
        
        self.volume_slider = FluentSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("75%")
        self.volume_slider.valueChanged.connect(lambda v: self.volume_label.setText(f"{v}%"))
        self.volume_slider.value_changing.connect(lambda v: self._log_slider_change("Volume", v))
        volume_layout.addWidget(self.volume_label)
        
        horizontal_layout.addLayout(volume_layout)
        
        # Temperature slider
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        
        self.temp_slider = FluentSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(10, 35)
        self.temp_slider.setValue(22)
        temp_layout.addWidget(self.temp_slider)
        
        self.temp_label = QLabel("22°C")
        self.temp_slider.valueChanged.connect(lambda v: self.temp_label.setText(f"{v}°C"))
        temp_layout.addWidget(self.temp_label)
        
        horizontal_layout.addLayout(temp_layout)
        layout.addWidget(horizontal_group)

        # Vertical sliders
        vertical_group = QGroupBox("Vertical Sliders")
        vertical_layout = QHBoxLayout(vertical_group)
        
        slider_configs = [
            ("Level 1", 0, 100, 30),
            ("Level 2", 0, 100, 60),
            ("Level 3", 0, 100, 90),
            ("Bass", -10, 10, 0),
            ("Treble", -10, 10, 2)
        ]
        
        self.vertical_sliders = []
        
        for i, (label_text, min_val, max_val, initial_val) in enumerate(slider_configs):
            slider_layout = QVBoxLayout()
            
            # Value label at top
            value_label = QLabel(str(initial_val))
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            slider_layout.addWidget(value_label)
            
            # Vertical slider
            v_slider = FluentSlider(Qt.Orientation.Vertical)
            v_slider.setRange(min_val, max_val)
            v_slider.setValue(initial_val)
            v_slider.valueChanged.connect(lambda v, lbl=value_label: lbl.setText(str(v)))
            slider_layout.addWidget(v_slider, 0, Qt.AlignmentFlag.AlignCenter)
            
            # Label at bottom
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            slider_layout.addWidget(label)
            
            self.vertical_sliders.append(v_slider)
            
            slider_widget = QWidget()
            slider_widget.setLayout(slider_layout)
            vertical_layout.addWidget(slider_widget)
        
        vertical_layout.addStretch()
        layout.addWidget(vertical_group)

        # Interactive slider controls
        interactive_group = QGroupBox("Interactive Slider Controls")
        interactive_layout = QVBoxLayout(interactive_group)
        
        # Main interactive slider
        main_slider_layout = QHBoxLayout()
        main_slider_layout.addWidget(QLabel("Interactive Slider:"))
        
        self.interactive_slider = FluentSlider(Qt.Orientation.Horizontal)
        self.interactive_slider.setRange(0, 1000)
        self.interactive_slider.setValue(500)
        main_slider_layout.addWidget(self.interactive_slider)
        
        self.interactive_value_label = QLabel("500")
        self.interactive_slider.valueChanged.connect(lambda v: self.interactive_value_label.setText(str(v)))
        main_slider_layout.addWidget(self.interactive_value_label)
        
        interactive_layout.addLayout(main_slider_layout)
        
        # Slider controls
        controls_grid = QGridLayout()
        
        # Range controls
        controls_grid.addWidget(QLabel("Minimum:"), 0, 0)
        self.slider_min_spinbox = QSpinBox()
        self.slider_min_spinbox.setRange(-1000, 1000)
        self.slider_min_spinbox.setValue(0)
        self.slider_min_spinbox.valueChanged.connect(self._update_slider_range)
        controls_grid.addWidget(self.slider_min_spinbox, 0, 1)
        
        controls_grid.addWidget(QLabel("Maximum:"), 0, 2)
        self.slider_max_spinbox = QSpinBox()
        self.slider_max_spinbox.setRange(-1000, 10000)
        self.slider_max_spinbox.setValue(1000)
        self.slider_max_spinbox.valueChanged.connect(self._update_slider_range)
        controls_grid.addWidget(self.slider_max_spinbox, 0, 3)
        
        # Step controls
        controls_grid.addWidget(QLabel("Single Step:"), 1, 0)
        self.slider_step_spinbox = QSpinBox()
        self.slider_step_spinbox.setRange(1, 100)
        self.slider_step_spinbox.setValue(1)
        self.slider_step_spinbox.valueChanged.connect(lambda v: self.interactive_slider.setSingleStep(v))
        controls_grid.addWidget(self.slider_step_spinbox, 1, 1)
        
        controls_grid.addWidget(QLabel("Page Step:"), 1, 2)
        self.slider_page_step_spinbox = QSpinBox()
        self.slider_page_step_spinbox.setRange(1, 1000)
        self.slider_page_step_spinbox.setValue(10)
        self.slider_page_step_spinbox.valueChanged.connect(lambda v: self.interactive_slider.setPageStep(v))
        controls_grid.addWidget(self.slider_page_step_spinbox, 1, 3)
        
        interactive_layout.addLayout(controls_grid)
        
        # Quick set buttons
        quick_set_layout = QHBoxLayout()
        
        quick_values = [0, 25, 50, 75, 100]
        for value in quick_values:
            btn = QPushButton(f"{value}%")
            btn.clicked.connect(
                lambda _, v=value: self.interactive_slider.setValue(
                    int(self.interactive_slider.maximum() * v / 100)
                )
            )
            quick_set_layout.addWidget(btn)
        
        quick_set_layout.addStretch()
        interactive_layout.addLayout(quick_set_layout)
        layout.addWidget(interactive_group)

        return widget

    def _create_range_sliders_demo(self) -> QWidget:
        """Create FluentRangeSlider demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Basic range sliders
        basic_range_group = QGroupBox("Basic Range Sliders")
        basic_range_layout = QVBoxLayout(basic_range_group)
        
        # Price range slider
        price_layout = QVBoxLayout()
        price_layout.addWidget(QLabel("Price Range ($):"))
        
        self.price_range_slider = FluentRangeSlider()
        self.price_range_slider.set_range(0, 1000)
        self.price_range_slider.set_values(200, 800)
        price_layout.addWidget(self.price_range_slider)
        
        self.price_range_label = QLabel("$200 - $800")
        self.price_range_slider.range_changed.connect(
            lambda min_val, max_val: self.price_range_label.setText(f"${min_val} - ${max_val}")
        )
        price_layout.addWidget(self.price_range_label)
        
        basic_range_layout.addLayout(price_layout)
        
        # Time range slider
        time_layout = QVBoxLayout()
        time_layout.addWidget(QLabel("Time Range (hours):"))
        
        self.time_range_slider = FluentRangeSlider()
        self.time_range_slider.set_range(0, 24)
        self.time_range_slider.set_values(9, 17)
        time_layout.addWidget(self.time_range_slider)
        
        self.time_range_label = QLabel("09:00 - 17:00")
        self.time_range_slider.range_changed.connect(self._update_time_range)
        time_layout.addWidget(self.time_range_label)
        
        basic_range_layout.addLayout(time_layout)
        
        # Temperature range slider
        temp_range_layout = QVBoxLayout()
        temp_range_layout.addWidget(QLabel("Temperature Range (°C):"))
        
        self.temp_range_slider = FluentRangeSlider()
        self.temp_range_slider.set_range(-10, 40)
        self.temp_range_slider.set_values(18, 25)
        temp_range_layout.addWidget(self.temp_range_slider)
        
        self.temp_range_label = QLabel("18°C - 25°C")
        self.temp_range_slider.range_changed.connect(
            lambda min_val, max_val: self.temp_range_label.setText(f"{min_val}°C - {max_val}°C")
        )
        temp_range_layout.addWidget(self.temp_range_label)
        
        basic_range_layout.addLayout(temp_range_layout)
        layout.addWidget(basic_range_group)

        # Interactive range slider
        interactive_range_group = QGroupBox("Interactive Range Slider")
        interactive_range_layout = QVBoxLayout(interactive_range_group)
        
        # Main range slider
        self.interactive_range_slider = FluentRangeSlider()
        self.interactive_range_slider.set_range(0, 100)
        self.interactive_range_slider.set_values(25, 75)
        interactive_range_layout.addWidget(self.interactive_range_slider)
        
        # Range display
        self.interactive_range_label = QLabel("25 - 75")
        self.interactive_range_slider.range_changed.connect(
            lambda min_val, max_val: self.interactive_range_label.setText(f"{min_val} - {max_val}")
        )
        interactive_range_layout.addWidget(self.interactive_range_label)
        
        # Range controls
        range_controls_grid = QGridLayout()
        
        # Total range controls
        range_controls_grid.addWidget(QLabel("Total Range Min:"), 0, 0)
        self.range_total_min_spinbox = QSpinBox()
        self.range_total_min_spinbox.setRange(-1000, 1000)
        self.range_total_min_spinbox.setValue(0)
        self.range_total_min_spinbox.valueChanged.connect(self._update_total_range)
        range_controls_grid.addWidget(self.range_total_min_spinbox, 0, 1)
        
        range_controls_grid.addWidget(QLabel("Total Range Max:"), 0, 2)
        self.range_total_max_spinbox = QSpinBox()
        self.range_total_max_spinbox.setRange(-1000, 10000)
        self.range_total_max_spinbox.setValue(100)
        self.range_total_max_spinbox.valueChanged.connect(self._update_total_range)
        range_controls_grid.addWidget(self.range_total_max_spinbox, 0, 3)
        
        # Selected range controls
        range_controls_grid.addWidget(QLabel("Selected Min:"), 1, 0)
        self.range_selected_min_spinbox = QSpinBox()
        self.range_selected_min_spinbox.setRange(0, 100) # Will be updated by _update_total_range
        self.range_selected_min_spinbox.setValue(25)
        self.range_selected_min_spinbox.valueChanged.connect(self._update_selected_range)
        range_controls_grid.addWidget(self.range_selected_min_spinbox, 1, 1)
        
        range_controls_grid.addWidget(QLabel("Selected Max:"), 1, 2)
        self.range_selected_max_spinbox = QSpinBox()
        self.range_selected_max_spinbox.setRange(0, 100) # Will be updated by _update_total_range
        self.range_selected_max_spinbox.setValue(75)
        self.range_selected_max_spinbox.valueChanged.connect(self._update_selected_range)
        range_controls_grid.addWidget(self.range_selected_max_spinbox, 1, 3)
        
        interactive_range_layout.addLayout(range_controls_grid)
        
        # Preset buttons
        preset_layout = QHBoxLayout()
        
        presets = [("Low", 10, 30), ("Medium", 40, 60), ("High", 70, 90), ("Full", 0, 100)]
        for name, min_val, max_val in presets:
            btn = QPushButton(name)
            btn.clicked.connect(
                lambda _, min_v=min_val, max_v=max_val:  # Use _ for checked
                self.interactive_range_slider.set_values(min_v, max_v)
            )
            preset_layout.addWidget(btn)
        preset_layout.addStretch()
        interactive_range_layout.addLayout(preset_layout)
        layout.addWidget(interactive_range_group)

        # Multiple range sliders showcase
        showcase_group = QGroupBox("Range Sliders Showcase")
        showcase_layout = QVBoxLayout(showcase_group)
        
        showcase_configs = [
            ("Age Range", 0, 100, 25, 65), ("Score Range", 0, 1000, 600, 900),
            ("Percentage Range", 0, 100, 20, 80), ("Year Range", 1900, 2024, 1990, 2020)
        ]
        
        for label_text, min_range, max_range, init_min, init_max in showcase_configs:
            showcase_item_layout = QVBoxLayout()
            
            showcase_item_layout.addWidget(QLabel(f"{label_text}:"))
            
            range_slider = FluentRangeSlider()
            range_slider.set_range(min_range, max_range)
            range_slider.set_values(init_min, init_max)
            showcase_item_layout.addWidget(range_slider)
            
            range_label = QLabel(f"{init_min} - {init_max}")
            range_slider.range_changed.connect(
                lambda min_v, max_v, lbl=range_label: lbl.setText(f"{min_v} - {max_v}")
            )
            showcase_item_layout.addWidget(range_label)
            
            showcase_layout.addLayout(showcase_item_layout)
        
        layout.addWidget(showcase_group)

        return widget

    def _create_indicators_demo(self) -> QWidget:
        """Create FluentProgressIndicator demonstration section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # Basic indicators
        basic_indicators_group = QGroupBox("Basic Progress Indicators")
        basic_indicators_layout = QVBoxLayout(basic_indicators_group)
        
        # Different progress states
        indicators_grid = QGridLayout()
        
        indicator_configs = [
            ("Download", 0),
            ("Upload", 45),
            ("Installation", 75),
            ("Completion", 100)
        ]
        
        self.demo_indicators = []
        
        for i, (title, value) in enumerate(indicator_configs):
            indicator = FluentProgressIndicator()
            indicator.set_title(title)
            indicator.set_value(value)
            
            indicators_grid.addWidget(indicator, i // 2, i % 2)
            self.demo_indicators.append(indicator)
        
        basic_indicators_layout.addLayout(indicators_grid)
        layout.addWidget(basic_indicators_group)

        # Indeterminate indicators
        indeterminate_indicators_group = QGroupBox("Indeterminate Progress Indicators")
        indeterminate_indicators_layout = QVBoxLayout(indeterminate_indicators_group)
        
        indeterminate_indicators_info = QLabel("Indicators for tasks with unknown duration")
        indeterminate_indicators_layout.addWidget(indeterminate_indicators_info)
        
        # Indeterminate indicators
        indeterminate_indicators_container = QVBoxLayout()
        
        indeterminate_configs = [
            "Scanning for files...",
            "Connecting to server...",
            "Processing data..."
        ]
        
        self.indeterminate_indicators = []
        
        for title in indeterminate_configs:
            indicator = FluentProgressIndicator()
            indicator.set_title(title)
            indicator.set_indeterminate(True) # Start as indeterminate
            
            indeterminate_indicators_container.addWidget(indicator)
            self.indeterminate_indicators.append(indicator)
        
        indeterminate_indicators_layout.addLayout(indeterminate_indicators_container)
        
        # Indeterminate controls
        indeterminate_controls = QHBoxLayout()
        
        start_indeterminate_btn = QPushButton("Start All")
        start_indeterminate_btn.clicked.connect(self._start_all_indicators)
        
        stop_indeterminate_btn = QPushButton("Stop All")
        stop_indeterminate_btn.clicked.connect(self._stop_all_indicators)
        
        toggle_indeterminate_btn = QPushButton("Toggle Mode")
        toggle_indeterminate_btn.clicked.connect(self._toggle_indicators_mode)
        
        indeterminate_controls.addWidget(start_indeterminate_btn)
        indeterminate_controls.addWidget(stop_indeterminate_btn)
        indeterminate_controls.addWidget(toggle_indeterminate_btn)
        indeterminate_controls.addStretch()
        
        indeterminate_indicators_layout.addLayout(indeterminate_controls)
        layout.addWidget(indeterminate_indicators_group)

        # Interactive indicator
        interactive_indicator_group = QGroupBox("Interactive Progress Indicator")
        interactive_indicator_layout = QVBoxLayout(interactive_indicator_group)
        
        # Main interactive indicator
        self.interactive_indicator = FluentProgressIndicator()
        self.interactive_indicator.set_title("Interactive Progress")
        self.interactive_indicator.set_value(30)
        interactive_indicator_layout.addWidget(self.interactive_indicator)
        
        # Indicator controls
        indicator_controls_grid = QGridLayout()
        
        # Title control
        indicator_controls_grid.addWidget(QLabel("Title:"), 0, 0)
        self.indicator_title_input = QLineEdit("Interactive Progress")
        self.indicator_title_input.textChanged.connect(
            lambda text: self.interactive_indicator.set_title(text)
        )
        indicator_controls_grid.addWidget(self.indicator_title_input, 0, 1, 1, 2)
        
        # Value control
        indicator_controls_grid.addWidget(QLabel("Value:"), 1, 0)
        self.indicator_value_slider = QSlider(Qt.Orientation.Horizontal)
        self.indicator_value_slider.setRange(0, 100)
        self.indicator_value_slider.setValue(30)
        self.indicator_value_slider.valueChanged.connect(
            lambda v: self.interactive_indicator.set_value(v)
        )
        indicator_controls_grid.addWidget(self.indicator_value_slider, 1, 1)
        
        self.indicator_value_spinbox = QSpinBox()
        self.indicator_value_spinbox.setRange(0, 100)
        self.indicator_value_spinbox.setValue(30)
        self.indicator_value_spinbox.valueChanged.connect(
            lambda v: (
                self.indicator_value_slider.setValue(v),
                self.interactive_indicator.set_value(v)
            )
        )
        indicator_controls_grid.addWidget(self.indicator_value_spinbox, 1, 2)
        
        # Mode control
        self.indicator_indeterminate_cb = QCheckBox("Indeterminate Mode")
        self.indicator_indeterminate_cb.toggled.connect(
            lambda checked: self.interactive_indicator.set_indeterminate(checked)
        )
        indicator_controls_grid.addWidget(self.indicator_indeterminate_cb, 2, 0, 1, 3)
        
        interactive_indicator_layout.addLayout(indicator_controls_grid)
        
        # Animation buttons
        animation_buttons_layout = QHBoxLayout()
        
        animate_buttons = [
            ("0%", 0),
            ("25%", 25),
            ("50%", 50),
            ("75%", 75),
            ("100%", 100)
        ]
        
        for text, value in animate_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(
                lambda _, v=value: (
                    self.indicator_value_slider.setValue(v),
                    self.indicator_value_spinbox.setValue(v),
                    self.interactive_indicator.set_value(v) # This will animate if component supports it
                )
            )
            animation_buttons_layout.addWidget(btn)
        
        animation_buttons_layout.addStretch()
        interactive_indicator_layout.addLayout(animation_buttons_layout)
        
        layout.addWidget(interactive_indicator_group)

        return widget

    def _create_real_world_demo(self) -> QWidget:
        """Create real-world examples section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)

        # File download simulation
        download_group = QGroupBox("File Download Simulation")
        download_layout = QVBoxLayout(download_group)
        
        # Download progress indicator
        self.download_indicator = FluentProgressIndicator()
        self.download_indicator.set_title("Download Progress")
        self.download_indicator.set_value(0)
        download_layout.addWidget(self.download_indicator)
        
        # Download details
        download_details_layout = QGridLayout()
        
        self.download_speed_label = QLabel("Speed: 0 MB/s")
        download_details_layout.addWidget(self.download_speed_label, 0, 0)
        
        self.download_size_label = QLabel("Size: 100 MB")
        download_details_layout.addWidget(self.download_size_label, 0, 1)
        
        self.download_eta_label = QLabel("ETA: --")
        download_details_layout.addWidget(self.download_eta_label, 0, 2)
        
        download_layout.addLayout(download_details_layout)
        
        # Download controls
        download_controls = QHBoxLayout()
        
        self.download_size_spinbox = QSpinBox()
        self.download_size_spinbox.setRange(1, 1000)
        self.download_size_spinbox.setValue(100)
        self.download_size_spinbox.setSuffix(" MB")
        
        start_download_btn = QPushButton("Start Download")
        start_download_btn.clicked.connect(self._start_download_simulation)
        
        self.stop_download_btn = QPushButton("Stop Download")
        self.stop_download_btn.clicked.connect(self._stop_download_simulation)
        self.stop_download_btn.setEnabled(False)
        
        download_controls.addWidget(QLabel("File Size:"))
        download_controls.addWidget(self.download_size_spinbox)
        download_controls.addWidget(start_download_btn)
        download_controls.addWidget(self.stop_download_btn)
        download_controls.addStretch()
        
        download_layout.addLayout(download_controls)
        layout.addWidget(download_group)

        # Multi-stage task simulation
        multistage_group = QGroupBox("Multi-Stage Task Simulation")
        multistage_layout = QVBoxLayout(multistage_group)
        
        # Stage progress
        self.stage_indicator = FluentProgressIndicator()
        self.stage_indicator.set_title("Initializing...")
        self.stage_indicator.set_value(0)
        multistage_layout.addWidget(self.stage_indicator)
        
        # Overall progress
        overall_layout = QHBoxLayout()
        overall_layout.addWidget(QLabel("Overall Progress:"))
        
        self.overall_progress = FluentProgressBar()
        self.overall_progress.setValue(0)
        overall_layout.addWidget(self.overall_progress)
        
        self.overall_percentage = QLabel("0%")
        overall_layout.addWidget(self.overall_percentage)
        
        multistage_layout.addLayout(overall_layout)
        
        # Stage controls
        stage_controls = QHBoxLayout()
        
        self.stage_duration_spinbox = QSpinBox()
        self.stage_duration_spinbox.setRange(1, 30)
        self.stage_duration_spinbox.setValue(5)
        self.stage_duration_spinbox.setSuffix(" seconds")
        
        start_stages_btn = QPushButton("Start Multi-Stage Task")
        start_stages_btn.clicked.connect(self._start_multistage_task)
        
        self.stop_stages_btn = QPushButton("Stop Task")
        self.stop_stages_btn.clicked.connect(self._stop_multistage_task)
        self.stop_stages_btn.setEnabled(False)
        
        stage_controls.addWidget(QLabel("Duration:"))
        stage_controls.addWidget(self.stage_duration_spinbox)
        stage_controls.addWidget(start_stages_btn)
        stage_controls.addWidget(self.stop_stages_btn)
        stage_controls.addStretch()
        
        multistage_layout.addLayout(stage_controls)
        layout.addWidget(multistage_group)

        # System monitoring simulation
        monitoring_group = QGroupBox("System Monitoring Simulation")
        monitoring_layout = QVBoxLayout(monitoring_group)
        
        # CPU usage
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU Usage:"))
        
        self.cpu_progress = FluentProgressBar()
        self.cpu_progress.setValue(25)
        cpu_layout.addWidget(self.cpu_progress)
        
        self.cpu_label = QLabel("25%")
        cpu_layout.addWidget(self.cpu_label)
        
        monitoring_layout.addLayout(cpu_layout)
        
        # Memory usage
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory Usage:"))
        
        self.memory_progress = FluentProgressBar()
        self.memory_progress.setValue(60)
        memory_layout.addWidget(self.memory_progress)
        
        self.memory_label = QLabel("60%")
        memory_layout.addWidget(self.memory_label)
        
        monitoring_layout.addLayout(memory_layout)
        
        # Disk usage
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(QLabel("Disk Usage:"))
        
        self.disk_progress = FluentProgressBar()
        self.disk_progress.setValue(80)
        disk_layout.addWidget(self.disk_progress)
        
        self.disk_label = QLabel("80%")
        disk_layout.addWidget(self.disk_label)
        
        monitoring_layout.addLayout(disk_layout)
        
        # Monitoring controls
        monitoring_controls = QHBoxLayout()
        
        start_monitoring_btn = QPushButton("Start Monitoring")
        start_monitoring_btn.clicked.connect(self._start_monitoring)
        
        stop_monitoring_btn = QPushButton("Stop Monitoring")
        stop_monitoring_btn.clicked.connect(self._stop_monitoring)
        
        monitoring_controls.addWidget(start_monitoring_btn)
        monitoring_controls.addWidget(stop_monitoring_btn)
        monitoring_controls.addStretch()
        
        monitoring_layout.addLayout(monitoring_controls)
        layout.addWidget(monitoring_group)

        # Audio equalizer simulation
        equalizer_group = QGroupBox("Audio Equalizer Simulation")
        equalizer_layout = QVBoxLayout() # Main layout for the group
        equalizer_group.setLayout(equalizer_layout) # Set layout for the group

        eq_container = QHBoxLayout() # Layout for the sliders themselves
        
        freq_bands = ["60Hz", "170Hz", "310Hz", "600Hz", "1kHz", "3kHz", "6kHz", "12kHz", "14kHz", "16kHz"]
        self.eq_sliders = []
        
        for band in freq_bands:
            band_layout = QVBoxLayout()
            gain_label = QLabel("0")
            gain_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            band_layout.addWidget(gain_label)
            eq_slider = FluentSlider(Qt.Orientation.Vertical)
            eq_slider.setRange(-12, 12)
            eq_slider.setValue(0)
            eq_slider.valueChanged.connect(lambda v, lbl=gain_label: lbl.setText(f"{v:+d}"))
            band_layout.addWidget(eq_slider, 0, Qt.AlignmentFlag.AlignCenter)
            freq_label = QLabel(band)
            freq_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            band_layout.addWidget(freq_label)
            self.eq_sliders.append(eq_slider)
            band_widget = QWidget()
            band_widget.setLayout(band_layout)
            eq_container.addWidget(band_widget)
        
        eq_container.addStretch()
        equalizer_layout.addLayout(eq_container) # Add sliders container to group's layout
        
        preset_controls = QHBoxLayout()
        eq_presets = [
            ("Flat", [0] * 10), ("Rock", [0, 0, -1, -1, 0, 2, 3, 3, 2, 1]),
            ("Pop", [-1, -1, 0, 2, 4, 4, 2, 0, -1, -1]), ("Jazz", [3, 2, 1, 1, 0, 0, 1, 2, 2, 3]),
            ("Classical", [4, 3, 2, 1, 0, 0, 1, 2, 3, 4])
        ]
        for preset_name, values in eq_presets:
            btn = QPushButton(preset_name)
            btn.clicked.connect(lambda _, vals=values: self._apply_eq_preset(vals)) # Use _ for checked
            preset_controls.addWidget(btn)
        preset_controls.addStretch()
        equalizer_layout.addLayout(preset_controls)
        layout.addWidget(equalizer_group)

        return widget # Ensure widget is returned

    def _create_interactive_demo(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        showcase_group = QGroupBox("All Components Interactive Showcase")
        showcase_layout = QVBoxLayout(showcase_group)
        master_layout = QHBoxLayout()
        master_layout.addWidget(QLabel("Master Control:"))
        self.master_slider = FluentSlider(Qt.Orientation.Horizontal)
        self.master_slider.setRange(0, 100)
        self.master_slider.setValue(50)
        master_layout.addWidget(self.master_slider)
        self.master_value_label = QLabel("50")
        self.master_slider.valueChanged.connect(lambda v: self.master_value_label.setText(str(v))) # Update label
        master_layout.addWidget(self.master_value_label)
        showcase_layout.addLayout(master_layout)
        sync_layout = QGridLayout()
        sync_layout.addWidget(QLabel("Progress Bar:"), 0, 0)
        self.sync_progress_bar = FluentProgressBar()
        self.sync_progress_bar.setValue(50)
        sync_layout.addWidget(self.sync_progress_bar, 0, 1)
        sync_layout.addWidget(QLabel("Progress Ring:"), 1, 0)
        self.sync_progress_ring = FluentProgressRing()
        self.sync_progress_ring.set_value(50)
        sync_layout.addWidget(self.sync_progress_ring, 1, 1, Qt.AlignmentFlag.AlignLeft)
        sync_layout.addWidget(QLabel("Range Slider:"), 2, 0)
        self.sync_range_slider = FluentRangeSlider()
        self.sync_range_slider.set_range(0, 100)
        self.sync_range_slider.set_values(25, 75)
        sync_layout.addWidget(self.sync_range_slider, 2, 1)
        sync_layout.addWidget(QLabel("Progress Indicator:"), 3, 0)
        self.sync_indicator = FluentProgressIndicator()
        self.sync_indicator.set_title("Synchronized Progress")
        self.sync_indicator.set_value(50)
        sync_layout.addWidget(self.sync_indicator, 3, 1)
        showcase_layout.addLayout(sync_layout)
        sync_controls = QHBoxLayout()
        self.enable_sync_cb = QCheckBox("Enable Synchronization")
        self.enable_sync_cb.setChecked(True)
        sync_controls.addWidget(self.enable_sync_cb)
        animate_sync_btn = QPushButton("Animate All")
        animate_sync_btn.clicked.connect(self._animate_all_components)
        sync_controls.addWidget(animate_sync_btn)
        random_sync_btn = QPushButton("Random Values")
        random_sync_btn.clicked.connect(self._randomize_all_components)
        sync_controls.addWidget(random_sync_btn)
        sync_controls.addStretch()
        showcase_layout.addLayout(sync_controls)
        layout.addWidget(showcase_group)

        performance_group = QGroupBox("Performance Test")
        performance_layout = QVBoxLayout(performance_group)
        performance_info = QLabel("Test performance with multiple animated components")
        performance_layout.addWidget(performance_info)
        perf_controls = QHBoxLayout()
        create_many_btn = QPushButton("Create 20 Components")
        create_many_btn.clicked.connect(self._create_many_components)
        animate_many_btn = QPushButton("Animate All")
        animate_many_btn.clicked.connect(self._animate_many_components)
        clear_many_btn = QPushButton("Clear")
        clear_many_btn.clicked.connect(self._clear_many_components)
        perf_controls.addWidget(create_many_btn)
        perf_controls.addWidget(animate_many_btn)
        perf_controls.addWidget(clear_many_btn)
        perf_controls.addStretch()
        performance_layout.addLayout(perf_controls)
        self.many_components_scroll = QScrollArea()
        self.many_components_widget = QWidget()
        self.many_components_layout = QGridLayout(self.many_components_widget)
        self.many_components_scroll.setWidget(self.many_components_widget)
        self.many_components_scroll.setWidgetResizable(True)
        self.many_components_scroll.setMaximumHeight(200) # Or set a fixed height
        performance_layout.addWidget(self.many_components_scroll)
        layout.addWidget(performance_group)
        self._setup_event_log(layout)
        return widget

    def _setup_event_log(self, parent_layout):
        """Setup event logging"""
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout(log_group)
        
        self.event_log = QTextEdit()
        self.event_log.setMaximumHeight(100)
        self.event_log.setPlaceholderText("Component events will be logged here...")
        self.event_log.setReadOnly(True)
        log_layout.addWidget(self.event_log)
        
        log_controls = QHBoxLayout()
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.event_log.clear)
        log_controls.addWidget(clear_log_btn)
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        parent_layout.addWidget(log_group)

    def _log_event(self, event_type: str, details: str):
        """Log component events"""
        from datetime import datetime # Import here or at top if used elsewhere
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {event_type}: {details}")

    def _log_slider_change(self, source: str, value: int):
        self._log_event("Slider Value Changing", f"{source} to {value}")

    def _start_all_indeterminate(self):
        for bar in self.indeterminate_bars:
            bar.set_indeterminate(True)
        self._log_event("Progress Bar", "Started all indeterminate bars")

    def _stop_all_indeterminate(self):
        for bar in self.indeterminate_bars:
            bar.set_indeterminate(False)
            # bar.setValue(0) # Optionally reset value
        self._log_event("Progress Bar", "Stopped all indeterminate bars")

    def _toggle_indeterminate(self):
        if not self.indeterminate_bars:
            self._log_event("Progress Bar", "No indeterminate bars to toggle.")
            return
        # Assuming FluentProgressBar has a way to check its state, e.g. `_is_indeterminate`
        # This might need to be exposed via a public method like `is_indeterminate()`
        current_state = self.indeterminate_bars[0]._is_indeterminate 
        new_state = not current_state
        for bar in self.indeterminate_bars:
            bar.set_indeterminate(new_state)
        self._log_event("Progress Bar", f"Toggled indeterminate state to {new_state}")

    def _animate_to_value(self):
        target = self.target_value_spinbox.value()
        self.animated_progress.set_value_animated(target)
        self._log_event("Animation", f"Animating progress bar to {target}%")

    def _random_animation(self):
        target = random.randint(0, 100)
        self.target_value_spinbox.setValue(target)
        self.animated_progress.set_value_animated(target)
        self._log_event("Animation", f"Random animation for progress bar to {target}%")

    def _start_auto_updates(self):
        if not hasattr(self, 'slow_auto_timer') or not self.slow_auto_timer.isActive():
            self.slow_auto_timer = QTimer(self)
            self.slow_auto_timer.timeout.connect(self._update_slow_progress)
            self.slow_auto_timer.start(2000 // 100) # Approx 2s cycle, update every 20ms
            if self.slow_auto_timer not in self.timers: self.timers.append(self.slow_auto_timer)
        
        if not hasattr(self, 'fast_auto_timer') or not self.fast_auto_timer.isActive():
            self.fast_auto_timer = QTimer(self)
            self.fast_auto_timer.timeout.connect(self._update_fast_progress)
            self.fast_auto_timer.start(500 // 100) # Approx 0.5s cycle, update every 5ms
            if self.fast_auto_timer not in self.timers: self.timers.append(self.fast_auto_timer)
        self._log_event("Auto Update", "Started auto updates for progress bars")

    def _stop_auto_updates(self):
        if hasattr(self, 'slow_auto_timer'): self.slow_auto_timer.stop()
        if hasattr(self, 'fast_auto_timer'): self.fast_auto_timer.stop()
        self.timers = [t for t in self.timers if t.isActive()] # Clean up timers list
        self._log_event("Auto Update", "Stopped auto updates for progress bars")

    def _update_slow_progress(self):
        current = self.slow_auto_progress.value()
        new_value = (current + 1) % (self.slow_auto_progress.maximum() + 1)
        self.slow_auto_progress.setValue(new_value)

    def _update_fast_progress(self):
        current = self.fast_auto_progress.value()
        new_value = (current + 5) % (self.fast_auto_progress.maximum() + 1) # Faster increment
        self.fast_auto_progress.setValue(new_value)

    def _start_all_rings(self):
        for ring in self.indeterminate_rings:
            ring.set_indeterminate(True)
        self._log_event("Progress Ring", "Started all indeterminate rings")

    def _stop_all_rings(self):
        """Stop all indeterminate rings"""
        for ring in self.indeterminate_rings:
            ring.set_indeterminate(False)
            # ring.set_value(0) # Optionally reset value
        self._log_event("Progress Ring", "Stopped all indeterminate rings")

    def _update_ring_value(self, value):
        self.interactive_ring.set_value(value)
        self.ring_value_label.setText(str(value))
        self._log_event("Ring Control", f"Ring value set to {value}")

    def _update_ring_maximum(self, value):
        if value <= 0: return # Max must be > 0
        self.interactive_ring.set_maximum(value)
        self.ring_value_slider.setMaximum(value)
        # Adjust current value if it exceeds new maximum
        if self.interactive_ring.value() > value:
            self.interactive_ring.set_value(value)
            self.ring_value_slider.setValue(value)
        self._log_event("Ring Control", f"Ring maximum set to {value}")

    def _toggle_ring_mode(self, checked):
        self.interactive_ring.set_indeterminate(checked)
        self.ring_value_slider.setEnabled(not checked)
        self.ring_max_spinbox.setEnabled(not checked) # Also disable max if indeterminate
        self._log_event("Ring Control", f"Ring indeterminate mode: {checked}")

    def _animate_ring_to(self, value):
        # FluentProgressRing does not have a specific "set_value_animated"
        # It might have internal animation on set_value, or not.
        self.interactive_ring.set_value(value)
        self.ring_value_slider.setValue(value) # Keep slider in sync
        self._log_event("Ring Animation", f"Set ring value to {value}")

    def _update_slider_range(self):
        min_val = self.slider_min_spinbox.value()
        max_val = self.slider_max_spinbox.value()
        if min_val < max_val:
            self.interactive_slider.setRange(min_val, max_val)
            # Adjust current value if it's outside new range
            current_val = self.interactive_slider.value()
            if current_val < min_val: self.interactive_slider.setValue(min_val)
            if current_val > max_val: self.interactive_slider.setValue(max_val)
            self._log_event("Slider Control", f"Interactive slider range: {min_val}-{max_val}")
        else:
            self._log_event("Slider Control", "Invalid range (min >= max)")


    def _update_time_range(self, min_val, max_val):
        self.time_range_label.setText(f"{min_val:02d}:00 - {max_val:02d}:00")
        self._log_event("Range Slider", f"Time range: {min_val:02d}:00 - {max_val:02d}:00")

    def _update_total_range(self):
        min_total = self.range_total_min_spinbox.value()
        max_total = self.range_total_max_spinbox.value()
        if min_total < max_total:
            self.interactive_range_slider.set_range(min_total, max_total)
            # Update limits for selected range spinboxes
            self.range_selected_min_spinbox.setRange(min_total, max_total)
            self.range_selected_max_spinbox.setRange(min_total, max_total)
            # Adjust current selected values if they are outside new total range
            cur_sel_min, cur_sel_max = self.interactive_range_slider.get_values()
            new_sel_min = max(min_total, min(cur_sel_min, max_total))
            new_sel_max = max(min_total, min(cur_sel_max, max_total))
            if new_sel_min > new_sel_max: new_sel_min = new_sel_max # Ensure min <= max
            
            self.interactive_range_slider.set_values(new_sel_min, new_sel_max)
            self.range_selected_min_spinbox.setValue(new_sel_min)
            self.range_selected_max_spinbox.setValue(new_sel_max)

            self._log_event("Range Slider Control", f"Total range: {min_total}-{max_total}")
        else:
            self._log_event("Range Slider Control", "Invalid total range (min >= max)")


    def _update_selected_range(self):
        min_sel = self.range_selected_min_spinbox.value()
        max_sel = self.range_selected_max_spinbox.value()
        
        # Ensure min_sel <= max_sel, adjust if necessary
        # For example, if min_sel spinbox is changed to be > max_sel, adjust max_sel
        sender = self.sender()
        if sender == self.range_selected_min_spinbox and min_sel > max_sel:
            max_sel = min_sel
            self.range_selected_max_spinbox.setValue(max_sel)
        elif sender == self.range_selected_max_spinbox and max_sel < min_sel:
            min_sel = max_sel
            self.range_selected_min_spinbox.setValue(min_sel)

        # Ensure selected range is within the total range of the slider
        total_min, total_max = self.interactive_range_slider._min_value, self.interactive_range_slider._max_value
        min_sel = max(total_min, min(min_sel, total_max))
        max_sel = max(total_min, min(max_sel, total_max))
        
        if min_sel > max_sel: # Final check
             min_sel = max_sel 
             self.range_selected_min_spinbox.setValue(min_sel)


        self.interactive_range_slider.set_values(min_sel, max_sel)
        self._log_event("Range Slider Control", f"Selected range: {min_sel}-{max_sel}")


    def _start_all_indicators(self):
        for indicator in self.indeterminate_indicators:
            indicator.set_indeterminate(True)
        self._log_event("Indicator", "Started all indeterminate indicators")

    def _stop_all_indicators(self):
        for indicator in self.indeterminate_indicators:
            indicator.set_indeterminate(False)
            # indicator.set_value(0) # Optionally reset
        self._log_event("Indicator", "Stopped all indeterminate indicators")

    def _toggle_indicators_mode(self):
        if not self.indeterminate_indicators:
            self._log_event("Indicator", "No indeterminate indicators to toggle.")
            return
        # Assuming FluentProgressIndicator's progress_bar._is_indeterminate can be checked
        current_state = self.indeterminate_indicators[0].progress_bar._is_indeterminate
        new_state = not current_state
        for indicator in self.indeterminate_indicators:
            indicator.set_indeterminate(new_state)
        self._log_event("Indicator", f"Toggled indicators indeterminate mode to {new_state}")


    def _start_download_simulation(self):
        if hasattr(self, 'download_thread_worker') and self.download_thread_worker.isRunning():
            self._log_event("Download", "Download already in progress.")
            return

        file_size = self.download_size_spinbox.value()
        self.download_size_label.setText(f"Size: {file_size} MB")
        self.download_indicator.set_value(0)
        self.download_indicator.set_indeterminate(False)
        self.download_speed_label.setText("Speed: ...")
        self.download_eta_label.setText("ETA: ...")

        self.download_thread_worker = FileDownloadSimulator(file_size_mb=file_size)
        self.download_thread_worker.progress_updated.connect(self.download_indicator.set_value)
        self.download_thread_worker.progress_updated.connect(self._update_download_eta)
        self.download_thread_worker.speed_changed.connect(self.download_speed_label.setText) # speed_changed emits string
        self.download_thread_worker.finished_download.connect(self._on_download_finished)
        
        self.download_thread_worker.start()
        self.stop_download_btn.setEnabled(True)
        # self.start_download_btn.setEnabled(False) # Optional: disable start while running
        self._log_event("Download", f"Started download: {file_size}MB")

    def _update_download_eta(self, progress_percent):
        # This is a placeholder. Real ETA calculation is complex.
        if 0 < progress_percent < 100:
            self.download_eta_label.setText(f"ETA: {(100 - progress_percent) // 2}s (est.)")
        elif progress_percent == 100:
             self.download_eta_label.setText("ETA: Done")
        else:
            self.download_eta_label.setText("ETA: --")


    def _stop_download_simulation(self):
        if hasattr(self, 'download_thread_worker') and self.download_thread_worker.isRunning():
            self.download_thread_worker.stop_download()
            # self.download_thread_worker.wait() # Optional: wait for thread to truly finish
            self.stop_download_btn.setEnabled(False)
            # self.start_download_btn.setEnabled(True)
            self.download_indicator.set_title("Download Stopped")
            self._log_event("Download", "Stopped download simulation")
        else:
            self._log_event("Download", "No active download to stop")


    def _on_download_finished(self):
        self.download_indicator.set_title("Download Complete")
        self.download_indicator.set_value(100)
        self.stop_download_btn.setEnabled(False)
        # self.start_download_btn.setEnabled(True)
        self.download_eta_label.setText("ETA: Done")
        self._log_event("Download", "Download finished")


    def _start_multistage_task(self):
        if hasattr(self, 'multistage_task_worker') and self.multistage_task_worker.isRunning():
            self._log_event("Multi-Stage", "Task already in progress.")
            return

        duration = self.stage_duration_spinbox.value()
        self.stage_indicator.set_value(0) # Reset progress
        self.overall_progress.setValue(0)
        self.overall_percentage.setText("0%")

        self.multistage_task_worker = WorkerThread(duration=duration)
        self.multistage_task_worker.progress_updated.connect(self._update_overall_progress)
        self.multistage_task_worker.stage_changed.connect(self.stage_indicator.set_title)
        # If stage_indicator should also show overall progress:
        self.multistage_task_worker.progress_updated.connect(self.stage_indicator.set_value)
        self.multistage_task_worker.finished_work.connect(self._on_multistage_finished)
        
        self.multistage_task_worker.start()
        self.stop_stages_btn.setEnabled(True)
        self._log_event("Multi-Stage", f"Started task (duration: {duration}s)")

    def _update_overall_progress(self, value):
        self.overall_progress.setValue(value)
        self.overall_percentage.setText(f"{value}%")
        # If stage_indicator also shows overall progress:
        # self.stage_indicator.set_value(value)


    def _stop_multistage_task(self):
        if hasattr(self, 'multistage_task_worker') and self.multistage_task_worker.isRunning():
            self.multistage_task_worker.stop_work()
            self.stop_stages_btn.setEnabled(False)
            self.stage_indicator.set_title("Task Stopped")
            self._log_event("Multi-Stage", "Task stopped")
        else:
            self._log_event("Multi-Stage", "No active task to stop")


    def _on_multistage_finished(self):
        self.stage_indicator.set_title("Task Complete")
        self.overall_progress.setValue(100)
        self.overall_percentage.setText("100%")
        self.stage_indicator.set_value(100)
        self.stop_stages_btn.setEnabled(False)
        self._log_event("Multi-Stage", "Task finished")


    def _start_monitoring(self):
        if hasattr(self, 'monitoring_timer') and self.monitoring_timer.isActive():
            self._log_event("Monitoring", "Already monitoring.")
            return
            
        self.monitoring_timer = QTimer(self)
        self.monitoring_timer.timeout.connect(self._update_monitoring_values)
        self.monitoring_timer.start(1000) # Update every second
        if self.monitoring_timer not in self.timers: self.timers.append(self.monitoring_timer)
        self._log_event("Monitoring", "Started monitoring")

    def _update_monitoring_values(self):
        cpu = random.randint(5, 95)
        mem = random.randint(20, 80)
        disk = random.randint(10, 90)
        self.cpu_progress.setValue(cpu)
        self.cpu_label.setText(f"{cpu}%")
        self.memory_progress.setValue(mem)
        self.memory_label.setText(f"{mem}%")
        self.disk_progress.setValue(disk)
        self.disk_label.setText(f"{disk}%")
        # self._log_event("Monitoring", f"Update: CPU {cpu}%, Mem {mem}%, Disk {disk}%") # Can be too verbose


    def _stop_monitoring(self):
        if hasattr(self, 'monitoring_timer') and self.monitoring_timer.isActive():
            self.monitoring_timer.stop()
            self._log_event("Monitoring", "Stopped monitoring")
        else:
            self._log_event("Monitoring", "Not currently monitoring")


    def _apply_eq_preset(self, values):
        if len(self.eq_sliders) == len(values):
            for slider, value in zip(self.eq_sliders, values):
                slider.setValue(value)
            self._log_event("Equalizer", f"Applied preset.")
        else:
            self._log_event("Equalizer", "Preset length mismatch.")


    def _update_all_components(self, value):
        # self.master_value_label.setText(str(value)) # Already connected directly
        if self.enable_sync_cb.isChecked():
            self.sync_progress_bar.setValue(value)
            self.sync_progress_ring.set_value(value)
            
            # For range slider, map master value to a range
            # Example: min is value/2, max is value/2 + 30 (capped)
            min_val = value // 2
            max_val = min(min_val + 30, self.sync_range_slider._max_value) # Assuming _max_value is total max
            if min_val > max_val : min_val = max_val -1 # ensure min <= max
            if min_val < self.sync_range_slider._min_value : min_val = self.sync_range_slider._min_value

            self.sync_range_slider.set_values(min_val, max_val)
            self.sync_indicator.set_value(value)
            self._log_event("Interactive Sync", f"Components synced to master value {value}")

    def _animate_all_components(self):
        target = random.randint(0, 100)
        self.master_slider.setValue(target) # This will trigger _update_all_components if sync is on
        
        # If sync is off, or for components with their own animation independent of master_slider's direct value
        if hasattr(self.sync_progress_bar, 'set_value_animated'):
            self.sync_progress_bar.set_value_animated(target)
        else:
            self.sync_progress_bar.setValue(target)
        
        self.sync_progress_ring.set_value(target) # No specific animation method
        
        min_val = target // 2
        max_val = min(min_val + 30, self.sync_range_slider._max_value)
        if min_val > max_val : min_val = max_val -1
        if min_val < self.sync_range_slider._min_value : min_val = self.sync_range_slider._min_value
        self.sync_range_slider.set_values(min_val, max_val) # No specific animation method

        self.sync_indicator.set_value(target) # Uses internal animated bar

        self._log_event("Interactive Sync", f"Animated all components towards {target}")


    def _randomize_all_components(self):
        master_val = random.randint(0,100)
        self.master_slider.setValue(master_val) # Will sync if checkbox is checked

        if not self.enable_sync_cb.isChecked(): # If not syncing, randomize individually
            self.sync_progress_bar.setValue(random.randint(0,100))
            self.sync_progress_ring.set_value(random.randint(0,100))
            min_r, max_r = sorted([random.randint(0,100), random.randint(0,100)])
            if min_r == max_r and max_r < 100: max_r +=1
            elif min_r == max_r and min_r > 0: min_r -=1
            self.sync_range_slider.set_values(min_r, max_r)
            self.sync_indicator.set_value(random.randint(0,100))
        self._log_event("Interactive Sync", "Randomized component values")


    def _create_many_components(self):
        self._clear_many_components() # Clear previous ones first
        self.many_components_list = [] 
        for i in range(20):
            row, col = divmod(i, 4) # 5 rows, 4 columns
            comp_type = random.choice([FluentProgressBar, FluentProgressRing, FluentSlider])
            
            if comp_type == FluentSlider:
                component = comp_type(Qt.Orientation.Horizontal)
                component.setRange(0,100)
            else:
                component = comp_type()
            
            if hasattr(component, 'setValue'): component.setValue(random.randint(0,100))
            elif hasattr(component, 'set_value'): component.set_value(random.randint(0,100))

            self.many_components_layout.addWidget(component, row, col)
            self.many_components_list.append(component)
        self._log_event("Performance", "Created 20 components")


    def _animate_many_components(self):
        if hasattr(self, 'many_components_list') and self.many_components_list:
            for comp in self.many_components_list:
                val = random.randint(0,100)
                if hasattr(comp, 'set_value_animated'): comp.set_value_animated(val)
                elif hasattr(comp, 'set_value'): comp.set_value(val) # For Ring, Slider
                elif hasattr(comp, 'setValue'): comp.setValue(val) # Fallback
            self._log_event("Performance", "Animated many components")
        else:
            self._log_event("Performance", "No components to animate. Create first.")


    def _clear_many_components(self):
        if hasattr(self, 'many_components_list'):
            for component in self.many_components_list:
                component.deleteLater()
            self.many_components_list.clear()
        
        # Also clear from layout
        while self.many_components_layout.count():
            item = self.many_components_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._log_event("Performance", "Cleared many components")


    def _toggle_theme(self, theme_name: str):
        if theme_name == "Dark":
            theme_manager.set_theme_mode(ThemeMode.DARK)
        else:
            theme_manager.set_theme_mode(ThemeMode.LIGHT)
        self._log_event("Theme", f"Switched to {theme_name} mode")

    def closeEvent(self, event):
        """Ensure threads and timers are stopped on close."""
        self._stop_auto_updates()
        self._stop_monitoring()
        if hasattr(self, 'download_thread_worker') and self.download_thread_worker.isRunning():
            self.download_thread_worker.stop_download()
            self.download_thread_worker.wait(1000) # Wait a bit
        if hasattr(self, 'multistage_task_worker') and self.multistage_task_worker.isRunning():
            self.multistage_task_worker.stop_work()
            self.multistage_task_worker.wait(1000)

        for timer in self.timers: # Stop any other managed timers
            timer.stop()
        self.timers.clear()
        
        # Clean up worker_threads if used
        for worker in self.worker_threads:
            if worker.isRunning():
                if hasattr(worker, 'should_stop'): worker.should_stop = True
                elif hasattr(worker, 'stop_work'): worker.stop_work()
                elif hasattr(worker, 'stop_download'): worker.stop_download()
                worker.wait(500)
        self.worker_threads.clear()

        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Apply initial theme before creating window
    # theme_manager.set_theme_mode(ThemeMode.DARK) # Or LIGHT
    window = ProgressDemo()
    window.show()
    sys.exit(app.exec())