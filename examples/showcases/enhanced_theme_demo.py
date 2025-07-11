"""
Enhanced Theme Integration Demo
Demonstrates the comprehensive theme system with animations, transitions, and component integration
"""

import sys
from typing import Optional
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QLabel, QComboBox, QCheckBox,
                               QScrollArea, QFrame, QGroupBox, QGridLayout, QSpacerItem,
                               QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# Import our enhanced theme system
sys.path.append('d:/Project/simple-fluent-widget')
from core.theme import get_theme_manager, ThemeMode, ThemeTransitionType
from core.theme_integration_fixed import (ThemeAwareButton, ThemeAwareToggle, 
                                        ThemeAwareContainer, get_transition_coordinator)
from core.enhanced_base import (FluentComponentFactory, ThemeIntegratedFluentButton,
                              ThemeIntegratedContainer)
from core.enhanced_animations import get_theme_aware_animation


class ThemeIntegrationDemo(QMainWindow):
    """Comprehensive demo of the enhanced theme integration system"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Theme Integration Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Get theme system instances
        self.theme_manager = get_theme_manager()
        self.transition_coordinator = get_transition_coordinator()
        self.theme_animation = get_theme_aware_animation()
        
        # Component storage for demonstrations
        self.theme_components = []
        
        self._setup_ui()
        self._connect_signals()
        
        # Apply initial theme
        self.theme_manager.set_theme_mode(ThemeMode.LIGHT)
    
    def _setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Enhanced Theme Integration Demo")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title)
        
        # Theme controls
        controls_section = self._create_theme_controls()
        main_layout.addWidget(controls_section)
        
        # Demo sections in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        demo_widget = QWidget()
        demo_layout = QVBoxLayout(demo_widget)
        demo_layout.setSpacing(30)
        
        # Add demo sections
        demo_layout.addWidget(self._create_button_demo())
        demo_layout.addWidget(self._create_container_demo())
        demo_layout.addWidget(self._create_animation_demo())
        demo_layout.addWidget(self._create_transition_demo())
        
        demo_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, 
                                       QSizePolicy.Policy.Expanding))
        
        scroll_area.setWidget(demo_widget)
        main_layout.addWidget(scroll_area)
    
    def _create_theme_controls(self) -> QGroupBox:
        """Create theme control section"""
        controls_group = QGroupBox("Theme Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        # Theme mode selector
        mode_label = QLabel("Theme Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Light", "Dark", "Auto"])
        
        # Transition type selector
        transition_label = QLabel("Transition Type:")
        self.transition_combo = QComboBox()
        self.transition_combo.addItems(["Instant", "Fade", "Slide", "Morph"])
        
        # Animation toggle
        self.animation_toggle = QCheckBox("Enable Animations")
        self.animation_toggle.setChecked(True)
        
        # Apply button
        apply_btn = QPushButton("Apply Theme Change")
        apply_btn.clicked.connect(self._apply_theme_change)
        
        # Coordinated transition button
        coord_btn = QPushButton("Coordinated Transition")
        coord_btn.clicked.connect(self._trigger_coordinated_transition)
        
        controls_layout.addWidget(mode_label)
        controls_layout.addWidget(self.mode_combo)
        controls_layout.addWidget(transition_label)
        controls_layout.addWidget(self.transition_combo)
        controls_layout.addWidget(self.animation_toggle)
        controls_layout.addWidget(apply_btn)
        controls_layout.addWidget(coord_btn)
        controls_layout.addStretch()
        
        return controls_group
    
    def _create_button_demo(self) -> QGroupBox:
        """Create button demonstration section"""
        group = QGroupBox("Theme-Integrated Buttons")
        layout = QGridLayout(group)
        
        # Different button variants
        variants = [
            ("Primary", FluentComponentFactory.create_button("Primary", "primary")),
            ("Secondary", FluentComponentFactory.create_button("Secondary", "secondary")),
            ("Success", FluentComponentFactory.create_button("Success", "success")),
            ("Danger", FluentComponentFactory.create_button("Danger", "danger")),
        ]
        
        for i, (label, button) in enumerate(variants):
            layout.addWidget(QLabel(label), i, 0)
            layout.addWidget(button, i, 1)
            self.theme_components.append(button)
            
            # Register with transition coordinator
            self.transition_coordinator.register_widget(button)
        
        # Theme-aware toggles
        for i in range(3):
            toggle = ThemeAwareToggle()
            layout.addWidget(QLabel(f"Toggle {i+1}"), i, 2)
            layout.addWidget(toggle, i, 3)
            self.theme_components.append(toggle)
            self.transition_coordinator.register_widget(toggle)
        
        return group
    
    def _create_container_demo(self) -> QGroupBox:
        """Create container demonstration section"""
        group = QGroupBox("Theme-Integrated Containers")
        layout = QHBoxLayout(group)
        
        # Different elevation levels
        for elevation in [1, 2, 4, 8]:
            container = FluentComponentFactory.create_container(elevation=elevation)
            container.setFixedSize(150, 120)
            
            # Add content to container
            container_layout = QVBoxLayout(container)
            container_layout.addWidget(QLabel(f"Elevation {elevation}"))
            container_layout.addWidget(QPushButton("Action"))
            
            layout.addWidget(container)
            self.theme_components.append(container)
            self.transition_coordinator.register_widget(container)
        
        # Card example
        card, card_layout = FluentComponentFactory.create_card("Sample Card", elevation=3)
        card.setFixedSize(200, 150)
        card_layout.addWidget(QLabel("Card content here"))
        card_layout.addWidget(QPushButton("Card Action"))
        
        layout.addWidget(card)
        self.theme_components.append(card)
        self.transition_coordinator.register_widget(card)
        
        return group
    
    def _create_animation_demo(self) -> QGroupBox:
        """Create animation demonstration section"""
        group = QGroupBox("Theme-Aware Animations")
        layout = QVBoxLayout(group)
        
        # Animation test buttons
        anim_layout = QHBoxLayout()
        
        color_anim_btn = QPushButton("Color Animation")
        color_anim_btn.clicked.connect(self._demo_color_animation)
        
        property_anim_btn = QPushButton("Property Animation")
        property_anim_btn.clicked.connect(self._demo_property_animation)
        
        cascade_anim_btn = QPushButton("Cascade Animation")
        cascade_anim_btn.clicked.connect(self._demo_cascade_animation)
        
        anim_layout.addWidget(color_anim_btn)
        anim_layout.addWidget(property_anim_btn)
        anim_layout.addWidget(cascade_anim_btn)
        
        layout.addLayout(anim_layout)
        
        # Animation target widget
        self.anim_target = ThemeAwareContainer()
        self.anim_target.setFixedSize(200, 100)
        target_layout = QVBoxLayout(self.anim_target)
        target_layout.addWidget(QLabel("Animation Target"))
        
        layout.addWidget(self.anim_target)
        self.theme_components.append(self.anim_target)
        
        return group
    
    def _create_transition_demo(self) -> QGroupBox:
        """Create transition demonstration section"""
        group = QGroupBox("Transition Effects")
        layout = QVBoxLayout(group)
        
        # Transition info
        info_label = QLabel("Use the controls above to test different transition types when changing themes.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Transition stats
        stats_layout = QHBoxLayout()
        
        self.registered_count_label = QLabel()
        self.animation_state_label = QLabel()
        
        stats_layout.addWidget(self.registered_count_label)
        stats_layout.addWidget(self.animation_state_label)
        
        layout.addLayout(stats_layout)
        
        # Update stats
        self._update_stats()
        
        return group
    
    def _connect_signals(self):
        """Connect theme system signals"""
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        self.theme_manager.transition_started.connect(self._on_transition_started)
        self.theme_manager.transition_finished.connect(self._on_transition_finished)
        
        # Update stats periodically
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_stats)
        self.stats_timer.start(1000)  # Update every second
    
    def _apply_theme_change(self):
        """Apply theme change based on controls"""
        # Get selected mode
        mode_text = self.mode_combo.currentText().lower()
        mode = ThemeMode.LIGHT
        if mode_text == "dark":
            mode = ThemeMode.DARK
        elif mode_text == "auto":
            mode = ThemeMode.AUTO
        
        # Get transition type
        transition_text = self.transition_combo.currentText().lower()
        transition_type = ThemeTransitionType.INSTANT
        if transition_text == "fade":
            transition_type = ThemeTransitionType.FADE
        elif transition_text == "slide":
            transition_type = ThemeTransitionType.SLIDE
        elif transition_text == "morph":
            transition_type = ThemeTransitionType.MORPH
        
        # Apply settings
        self.theme_manager.set_animation_enabled(self.animation_toggle.isChecked())
        self.theme_manager.set_transition_type(transition_type)
        self.theme_manager.set_theme_mode(mode)
    
    def _trigger_coordinated_transition(self):
        """Trigger coordinated transition across all components"""
        transition_text = self.transition_combo.currentText().lower()
        transition_type = ThemeTransitionType.FADE
        if transition_text == "slide":
            transition_type = ThemeTransitionType.SLIDE
        elif transition_text == "morph":
            transition_type = ThemeTransitionType.MORPH
        
        self.transition_coordinator.start_coordinated_transition(transition_type, stagger_delay=100)
    
    def _demo_color_animation(self):
        """Demonstrate color animation"""
        color_anim = self.theme_animation.create_theme_aware_color_animation(
            self.anim_target, "background-color", "primary", 500
        )
        color_anim.start()
    
    def _demo_property_animation(self):
        """Demonstrate property animation"""
        # This would be implemented with specific property animations
        pass
    
    def _demo_cascade_animation(self):
        """Demonstrate cascade animation"""
        for i, component in enumerate(self.theme_components[:5]):  # Animate first 5 components
            QTimer.singleShot(i * 100, lambda c=component: self._animate_component(c))
    
    def _animate_component(self, component):
        """Animate a single component"""
        if hasattr(component, '_on_theme_transition_started'):
            component._on_theme_transition_started("morph")
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme change"""
        print(f"Theme changed to: {theme_name}")
    
    def _on_transition_started(self, transition_type: str):
        """Handle transition start"""
        print(f"Transition started: {transition_type}")
    
    def _on_transition_finished(self):
        """Handle transition finish"""
        print("Transition finished")
    
    def _update_stats(self):
        """Update statistics display"""
        registered_count = len(self.transition_coordinator._registered_widgets)
        self.registered_count_label.setText(f"Registered Components: {registered_count}")
        
        animation_enabled = self.theme_manager._animation_enabled
        self.animation_state_label.setText(f"Animations: {'Enabled' if animation_enabled else 'Disabled'}")


def main():
    """Run the theme integration demo"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Enhanced Theme Integration Demo")
    app.setApplicationVersion("1.0")
    
    # Create and show demo window
    demo = ThemeIntegrationDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
