"""
FluentAvatar Component Example
Comprehensive demonstration of all avatar features
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QGridLayout, QFormLayout, QGroupBox,
                               QPushButton, QLabel, QLineEdit, QSpinBox,
                               QComboBox, QCheckBox, QRadioButton, QButtonGroup,
                               QSlider, QScrollArea, QTabWidget, QFileDialog,
                               QColorDialog, QTextEdit, QListWidget, QListWidgetItem,
                               QTableWidget, QTableWidgetItem, QSplitter,
                               QFrame, QProgressBar)
from PySide6.QtCore import Qt, QTimer, QElapsedTimer, Signal, QSize
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor, QPainter

from components.basic.avatar import FluentAvatar, FluentAvatarGroup
from core.theme import theme_manager


class AvatarDemoWidget(QWidget):
    """Widget demonstrating avatar functionalities"""

    def __init__(self):
        super().__init__()
        self.demo_avatars = []
        self.avatar_groups = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title = QLabel("FluentAvatar Component Showcase")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Create tabs for different features
        tab_widget = QTabWidget()

        # Basic Avatars Tab
        tab_widget.addTab(self._create_basic_avatars_tab(), "Basic Avatars")

        # Avatar Customization Tab
        tab_widget.addTab(self._create_customization_tab(), "Customization")

        # Avatar Groups Tab
        tab_widget.addTab(self._create_groups_tab(), "Avatar Groups")

        # Interactive Features Tab
        tab_widget.addTab(self._create_interactive_tab(), "Interactive")

        # Gallery & Examples Tab
        tab_widget.addTab(self._create_gallery_tab(), "Gallery")

        # Performance & Animation Tab
        tab_widget.addTab(self._create_performance_tab(), "Performance")

        layout.addWidget(tab_widget)

    def _create_basic_avatars_tab(self):
        """Create basic avatars demonstration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Size demonstration
        size_group = QGroupBox("Avatar Sizes")
        size_layout = QHBoxLayout(size_group)

        sizes = [
            ("Extra Small", FluentAvatar.Size.SMALL),
            ("Small", FluentAvatar.Size.MEDIUM),
            ("Medium", FluentAvatar.Size.LARGE),
            ("Large", FluentAvatar.Size.XLARGE),
            ("Extra Large", FluentAvatar.Size.XXLARGE)
        ]

        for size_name, size_enum in sizes:
            size_container = QVBoxLayout()

            # Create avatar with initials
            avatar = FluentAvatar(size=size_enum)
            avatar.setName("John Doe")
            size_container.addWidget(
                avatar, alignment=Qt.AlignmentFlag.AlignCenter)

            # Add label
            label = QLabel(f"{size_name}\n({size_enum.value}px)")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 11px; color: #666;")
            size_container.addWidget(label)

            size_layout.addLayout(size_container)

        layout.addWidget(size_group)

        # Shape demonstration
        shape_group = QGroupBox("Avatar Shapes")
        shape_layout = QHBoxLayout(shape_group)

        shapes = [
            ("Circle", FluentAvatar.Shape.CIRCLE),
            ("Rounded Square", FluentAvatar.Shape.ROUNDED_SQUARE),
            ("Square", FluentAvatar.Shape.SQUARE)
        ]

        for shape_name, shape_enum in shapes:
            shape_container = QVBoxLayout()

            # Create avatar with photo
            avatar = FluentAvatar(
                size=FluentAvatar.Size.LARGE, shape=shape_enum)
            avatar.setName("Alice Smith")
            shape_container.addWidget(
                avatar, alignment=Qt.AlignmentFlag.AlignCenter)

            # Add label
            label = QLabel(shape_name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 12px; font-weight: bold;")
            shape_container.addWidget(label)

            shape_layout.addLayout(shape_container)

        layout.addWidget(shape_group)

        # Style demonstration
        style_group = QGroupBox("Avatar Styles")
        style_layout = QGridLayout(style_group)

        # Initials avatar
        initials_container = QVBoxLayout()
        initials_avatar = FluentAvatar(size=FluentAvatar.Size.LARGE)
        initials_avatar.setInitials("AB")
        initials_container.addWidget(
            initials_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        initials_container.addWidget(
            QLabel("Initials"), alignment=Qt.AlignmentFlag.AlignCenter)
        style_layout.addLayout(initials_container, 0, 0)

        # Name-based avatar
        name_container = QVBoxLayout()
        name_avatar = FluentAvatar(size=FluentAvatar.Size.LARGE)
        name_avatar.setName("Charlie Brown")
        name_container.addWidget(
            name_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        name_container.addWidget(QLabel("Name-based"),
                                 alignment=Qt.AlignmentFlag.AlignCenter)
        style_layout.addLayout(name_container, 0, 1)

        # Icon avatar
        icon_container = QVBoxLayout()
        icon_avatar = FluentAvatar(size=FluentAvatar.Size.LARGE)
        icon_avatar.setIcon("user")
        icon_container.addWidget(
            icon_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        icon_container.addWidget(
            QLabel("Icon"), alignment=Qt.AlignmentFlag.AlignCenter)
        style_layout.addLayout(icon_container, 0, 2)

        # Placeholder avatar
        placeholder_container = QVBoxLayout()
        placeholder_avatar = FluentAvatar(size=FluentAvatar.Size.LARGE)
        placeholder_container.addWidget(
            placeholder_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        placeholder_container.addWidget(
            QLabel("Placeholder"), alignment=Qt.AlignmentFlag.AlignCenter)
        style_layout.addLayout(placeholder_container, 0, 3)

        layout.addWidget(style_group)

        # Border styles
        border_group = QGroupBox("Border Styles")
        border_layout = QHBoxLayout(border_group)

        border_styles = [
            ("No Border", 0, None),
            ("Thin Border", 1, QColor("#0078d4")),
            ("Medium Border", 2, QColor("#107c10")),
            ("Thick Border", 3, QColor("#d13438"))
        ]

        for border_name, width, color in border_styles:
            border_container = QVBoxLayout()

            avatar = FluentAvatar(size=FluentAvatar.Size.LARGE)
            avatar.setName("Demo User")
            avatar.setBorderWidth(width)
            if color:
                avatar.setBorderColor(color)

            border_container.addWidget(
                avatar, alignment=Qt.AlignmentFlag.AlignCenter)
            border_container.addWidget(
                QLabel(border_name), alignment=Qt.AlignmentFlag.AlignCenter)

            border_layout.addLayout(border_container)

        layout.addWidget(border_group)

        return widget

    def _create_customization_tab(self):
        """Create avatar customization tab"""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Left panel - Controls
        controls_panel = QWidget()
        controls_panel.setMaximumWidth(350)
        controls_layout = QVBoxLayout(controls_panel)

        # Avatar preview
        preview_group = QGroupBox("Live Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_avatar = FluentAvatar(size=FluentAvatar.Size.XXLARGE)
        self.preview_avatar.setName("Preview User")
        self.preview_avatar.setClickable(True)
        self.preview_avatar.clicked.connect(self._on_preview_clicked)

        preview_layout.addWidget(
            self.preview_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(preview_group)

        # Basic settings
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QFormLayout(basic_group)

        # Size selector
        self.size_combo = QComboBox()
        self.size_combo.addItems(["Small (24px)", "Medium (32px)", "Large (40px)",
                                 "X-Large (56px)", "XX-Large (72px)"])
        self.size_combo.setCurrentIndex(2)
        self.size_combo.currentIndexChanged.connect(self._update_preview_size)
        basic_layout.addRow("Size:", self.size_combo)

        # Shape selector
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Circle", "Rounded Square", "Square"])
        self.shape_combo.currentIndexChanged.connect(
            self._update_preview_shape)
        basic_layout.addRow("Shape:", self.shape_combo)

        # Name input
        self.name_input = QLineEdit("Preview User")
        self.name_input.textChanged.connect(self._update_preview_name)
        basic_layout.addRow("Name:", self.name_input)

        # Initials input
        self.initials_input = QLineEdit()
        self.initials_input.setMaxLength(2)
        self.initials_input.textChanged.connect(self._update_preview_initials)
        basic_layout.addRow("Custom Initials:", self.initials_input)

        # Clickable checkbox
        self.clickable_check = QCheckBox("Clickable")
        self.clickable_check.setChecked(True)
        self.clickable_check.toggled.connect(self._update_preview_clickable)
        basic_layout.addRow(self.clickable_check)

        controls_layout.addWidget(basic_group)

        # Border settings
        border_group = QGroupBox("Border Settings")
        border_layout = QFormLayout(border_group)

        # Border width
        self.border_width_spin = QSpinBox()
        self.border_width_spin.setRange(0, 10)
        self.border_width_spin.setValue(0)
        self.border_width_spin.valueChanged.connect(
            self._update_preview_border_width)
        border_layout.addRow("Border Width:", self.border_width_spin)

        # Border color
        self.border_color_btn = QPushButton("Choose Border Color")
        self.border_color_btn.clicked.connect(self._choose_border_color)
        self.border_color = QColor("#0078d4")
        self._update_border_color_button()
        border_layout.addRow(self.border_color_btn)

        controls_layout.addWidget(border_group)

        # Background settings
        bg_group = QGroupBox("Background Settings")
        bg_layout = QFormLayout(bg_group)

        # Auto color checkbox
        self.auto_color_check = QCheckBox("Auto-generate color from name")
        self.auto_color_check.setChecked(True)
        self.auto_color_check.toggled.connect(self._update_preview_auto_color)
        bg_layout.addRow(self.auto_color_check)

        # Custom background color
        self.bg_color_btn = QPushButton("Choose Background Color")
        self.bg_color_btn.clicked.connect(self._choose_bg_color)
        self.bg_color_btn.setEnabled(False)
        self.bg_color = QColor("#0078d4")
        bg_layout.addRow(self.bg_color_btn)

        controls_layout.addWidget(bg_group)

        # Photo settings
        photo_group = QGroupBox("Photo Settings")
        photo_layout = QVBoxLayout(photo_group)

        # Load photo button
        load_photo_btn = QPushButton("Load Photo")
        load_photo_btn.clicked.connect(self._load_photo)
        photo_layout.addWidget(load_photo_btn)

        # Generate demo photo button
        generate_photo_btn = QPushButton("Generate Demo Photo")
        generate_photo_btn.clicked.connect(self._generate_demo_photo)
        photo_layout.addWidget(generate_photo_btn)

        # Clear photo button
        clear_photo_btn = QPushButton("Clear Photo")
        clear_photo_btn.clicked.connect(self._clear_photo)
        photo_layout.addWidget(clear_photo_btn)

        controls_layout.addWidget(photo_group)

        # Action buttons
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)

        # Create avatar button
        create_avatar_btn = QPushButton("Create Avatar")
        create_avatar_btn.clicked.connect(self._create_custom_avatar)
        create_avatar_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        actions_layout.addWidget(create_avatar_btn)

        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_preview)
        actions_layout.addWidget(reset_btn)

        controls_layout.addWidget(actions_group)
        controls_layout.addStretch()

        layout.addWidget(controls_panel)

        # Right panel - Created avatars gallery
        gallery_panel = QWidget()
        gallery_layout = QVBoxLayout(gallery_panel)

        gallery_title = QLabel("Created Avatars Gallery")
        gallery_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        gallery_layout.addWidget(gallery_title)

        # Scroll area for avatars
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setSpacing(15)

        scroll_area.setWidget(self.gallery_widget)
        gallery_layout.addWidget(scroll_area)

        # Gallery controls
        gallery_controls = QHBoxLayout()

        clear_gallery_btn = QPushButton("Clear Gallery")
        clear_gallery_btn.clicked.connect(self._clear_gallery)
        gallery_controls.addWidget(clear_gallery_btn)

        gallery_controls.addStretch()

        gallery_count_label = QLabel("0 avatars")
        self.gallery_count_label = gallery_count_label
        gallery_controls.addWidget(gallery_count_label)

        gallery_layout.addLayout(gallery_controls)

        layout.addWidget(gallery_panel)

        return widget

    def _create_groups_tab(self):
        """Create avatar groups demonstration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Group controls
        controls_group = QGroupBox("Group Controls")
        controls_layout = QFormLayout(controls_group)

        # Max visible avatars
        self.max_visible_spin = QSpinBox()
        self.max_visible_spin.setRange(1, 10)
        self.max_visible_spin.setValue(5)
        self.max_visible_spin.valueChanged.connect(
            self._update_group_max_visible)
        controls_layout.addRow("Max Visible:", self.max_visible_spin)

        # Group size
        self.group_size_combo = QComboBox()
        self.group_size_combo.addItems(
            ["Small", "Medium", "Large", "X-Large", "XX-Large"])
        self.group_size_combo.setCurrentIndex(1)
        self.group_size_combo.currentIndexChanged.connect(
            self._update_group_size)
        controls_layout.addRow("Avatar Size:", self.group_size_combo)

        # Overlap
        self.overlap_spin = QSpinBox()
        self.overlap_spin.setRange(0, 20)
        self.overlap_spin.setValue(8)
        self.overlap_spin.valueChanged.connect(self._update_group_overlap)
        controls_layout.addRow("Overlap (px):", self.overlap_spin)

        layout.addWidget(controls_group)

        # Demo groups
        demo_groups_group = QGroupBox("Demo Groups")
        demo_groups_layout = QVBoxLayout(demo_groups_group)

        # Create sample groups
        self._create_sample_groups(demo_groups_layout)

        layout.addWidget(demo_groups_group)

        # Group management
        management_group = QGroupBox("Group Management")
        management_layout = QGridLayout(management_group)

        # Add avatar to group
        add_avatar_btn = QPushButton("Add Random Avatar")
        add_avatar_btn.clicked.connect(self._add_random_avatar_to_group)
        management_layout.addWidget(add_avatar_btn, 0, 0)

        # Remove avatar from group
        remove_avatar_btn = QPushButton("Remove Last Avatar")
        remove_avatar_btn.clicked.connect(self._remove_last_avatar_from_group)
        management_layout.addWidget(remove_avatar_btn, 0, 1)

        # Clear group
        clear_group_btn = QPushButton("Clear Group")
        clear_group_btn.clicked.connect(self._clear_demo_group)
        management_layout.addWidget(clear_group_btn, 0, 2)

        # Create new group
        new_group_btn = QPushButton("Create New Group")
        new_group_btn.clicked.connect(self._create_new_demo_group)
        management_layout.addWidget(new_group_btn, 1, 0)

        # Populate with team
        team_btn = QPushButton("Populate with Team")
        team_btn.clicked.connect(self._populate_with_team)
        management_layout.addWidget(team_btn, 1, 1)

        # Stress test
        stress_test_btn = QPushButton("Stress Test (20 avatars)")
        stress_test_btn.clicked.connect(self._stress_test_group)
        management_layout.addWidget(stress_test_btn, 1, 2)

        layout.addWidget(management_group)

        return widget

    def _create_interactive_tab(self):
        """Create interactive features tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Clickable avatars demo
        clickable_group = QGroupBox("Clickable Avatars")
        clickable_layout = QGridLayout(clickable_group)

        # Create clickable avatars with different actions
        actions = [
            ("Profile", "👤", self._show_profile_action),
            ("Settings", "⚙️", self._show_settings_action),
            ("Messages", "💬", self._show_messages_action),
            ("Notifications", "🔔", self._show_notifications_action)
        ]

        for i, (name, emoji, action) in enumerate(actions):
            container = QVBoxLayout()

            avatar = FluentAvatar(size=FluentAvatar.Size.LARGE)
            avatar.setName(name)
            avatar.setClickable(True)
            avatar.clicked.connect(action)

            container.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)
            container.addWidget(
                QLabel(f"{emoji} {name}"), alignment=Qt.AlignmentFlag.AlignCenter)

            clickable_layout.addLayout(container, i // 2, i % 2)

        layout.addWidget(clickable_group)

        # Animation demo
        animation_group = QGroupBox("Animation Demo")
        animation_layout = QVBoxLayout(animation_group)

        # Animation controls
        anim_controls = QHBoxLayout()

        pulse_btn = QPushButton("Pulse Animation")
        pulse_btn.clicked.connect(self._demo_pulse_animation)
        anim_controls.addWidget(pulse_btn)

        scale_btn = QPushButton("Scale Animation")
        scale_btn.clicked.connect(self._demo_scale_animation)
        anim_controls.addWidget(scale_btn)

        fade_btn = QPushButton("Fade Animation")
        fade_btn.clicked.connect(self._demo_fade_animation)
        anim_controls.addWidget(fade_btn)

        animation_layout.addLayout(anim_controls)

        # Animation target avatars
        self.animation_targets_layout = QHBoxLayout()
        self._create_animation_targets()
        animation_layout.addLayout(self.animation_targets_layout)

        layout.addWidget(animation_group)

        # State changes demo
        state_group = QGroupBox("State Changes Demo")
        state_layout = QVBoxLayout(state_group)

        # Create avatar for state demo
        self.state_demo_avatar = FluentAvatar(size=FluentAvatar.Size.XLARGE)
        self.state_demo_avatar.setName("State Demo")
        state_layout.addWidget(self.state_demo_avatar,
                               alignment=Qt.AlignmentFlag.AlignCenter)

        # State change controls
        state_controls = QGridLayout()

        name_btn = QPushButton("Change Name")
        name_btn.clicked.connect(self._demo_name_change)
        state_controls.addWidget(name_btn, 0, 0)

        initials_btn = QPushButton("Change Initials")
        initials_btn.clicked.connect(self._demo_initials_change)
        state_controls.addWidget(initials_btn, 0, 1)

        size_btn = QPushButton("Change Size")
        size_btn.clicked.connect(self._demo_size_change)
        state_controls.addWidget(size_btn, 1, 0)

        shape_btn = QPushButton("Change Shape")
        shape_btn.clicked.connect(self._demo_shape_change)
        state_controls.addWidget(shape_btn, 1, 1)

        border_btn = QPushButton("Toggle Border")
        border_btn.clicked.connect(self._demo_border_toggle)
        state_controls.addWidget(border_btn, 2, 0)

        color_btn = QPushButton("Random Color")
        color_btn.clicked.connect(self._demo_color_change)
        state_controls.addWidget(color_btn, 2, 1)

        state_layout.addLayout(state_controls)

        layout.addWidget(state_group)

        # Event log
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout(log_group)

        self.event_log = QTextEdit()
        self.event_log.setMaximumHeight(150)
        self.event_log.setReadOnly(True)
        log_layout.addWidget(self.event_log)

        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.event_log.clear)
        log_layout.addWidget(clear_log_btn)

        layout.addWidget(log_group)

        return widget

    def _create_gallery_tab(self):
        """Create gallery and examples tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Team gallery
        team_group = QGroupBox("Team Gallery Example")
        team_layout = QGridLayout(team_group)

        team_members = [
            ("John Smith", "Product Manager"),
            ("Sarah Johnson", "UX Designer"),
            ("Mike Chen", "Frontend Developer"),
            ("Emma Wilson", "Backend Developer"),
            ("David Brown", "QA Engineer"),
            ("Lisa Davis", "DevOps Engineer")
        ]

        for i, (name, role) in enumerate(team_members):
            member_layout = QVBoxLayout()

            avatar = FluentAvatar(size=FluentAvatar.Size.LARGE)
            avatar.setName(name)
            avatar.setClickable(True)
            avatar.clicked.connect(
                lambda n=name, r=role: self._show_member_details(n, r))

            member_layout.addWidget(
                avatar, alignment=Qt.AlignmentFlag.AlignCenter)
            member_layout.addWidget(
                QLabel(name), alignment=Qt.AlignmentFlag.AlignCenter)

            role_label = QLabel(role)
            role_label.setStyleSheet("color: #666; font-size: 11px;")
            member_layout.addWidget(
                role_label, alignment=Qt.AlignmentFlag.AlignCenter)

            team_layout.addLayout(member_layout, i // 3, i % 3)

        layout.addWidget(team_group)

        # User list example
        list_group = QGroupBox("User List Example")
        list_layout = QVBoxLayout(list_group)

        # Create user list
        user_list = QListWidget()
        user_list.setMaximumHeight(200)

        users = [
            "Alice Cooper", "Bob Johnson", "Carol White", "David Miller",
            "Eve Anderson", "Frank Taylor", "Grace Wilson", "Henry Moore"
        ]

        for user in users:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(10, 5, 10, 5)

            # Avatar
            avatar = FluentAvatar(size=FluentAvatar.Size.MEDIUM)
            avatar.setName(user)
            item_layout.addWidget(avatar)

            # User info
            info_layout = QVBoxLayout()
            name_label = QLabel(user)
            name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            status_label = QLabel("Online")
            status_label.setStyleSheet("color: #107c10; font-size: 9px;")

            info_layout.addWidget(name_label)
            info_layout.addWidget(status_label)
            item_layout.addLayout(info_layout)

            item_layout.addStretch()

            # Add to list
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            user_list.addItem(item)
            user_list.setItemWidget(item, item_widget)

        list_layout.addWidget(user_list)
        layout.addWidget(list_group)

        # Chat interface example
        chat_group = QGroupBox("Chat Interface Example")
        chat_layout = QVBoxLayout(chat_group)

        # Chat messages
        chat_area = QScrollArea()
        chat_area.setWidgetResizable(True)
        chat_area.setMaximumHeight(250)

        chat_widget = QWidget()
        chat_widget_layout = QVBoxLayout(chat_widget)

        messages = [
            ("Alice Cooper", "Hey everyone! How's the project going?", False),
            ("You", "Going great! Just finished the avatar component.", True),
            ("Bob Johnson", "Awesome work! The animations look smooth.", False),
            ("Carol White", "Can't wait to see it in action! 🎉", False),
        ]

        for sender, message, is_self in messages:
            msg_layout = QHBoxLayout()

            if not is_self:
                # Other person's message
                avatar = FluentAvatar(size=FluentAvatar.Size.SMALL)
                avatar.setName(sender)
                msg_layout.addWidget(avatar)

                msg_bubble = QLabel(f"{sender}: {message}")
                msg_bubble.setWordWrap(True)
                msg_bubble.setStyleSheet("""
                    background-color: #f3f2f1;
                    padding: 8px 12px;
                    border-radius: 12px;
                    max-width: 300px;
                """)
                msg_layout.addWidget(msg_bubble)
                msg_layout.addStretch()
            else:
                # Your message
                msg_layout.addStretch()

                msg_bubble = QLabel(message)
                msg_bubble.setWordWrap(True)
                msg_bubble.setStyleSheet("""
                    background-color: #0078d4;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 12px;
                    max-width: 300px;
                """)
                msg_layout.addWidget(msg_bubble)

                your_avatar = FluentAvatar(size=FluentAvatar.Size.SMALL)
                your_avatar.setInitials("YOU")
                msg_layout.addWidget(your_avatar)

            chat_widget_layout.addLayout(msg_layout)

        chat_area.setWidget(chat_widget)
        chat_layout.addWidget(chat_area)

        layout.addWidget(chat_group)

        return widget

    def _create_performance_tab(self):
        """Create performance and animation tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Performance metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QFormLayout(metrics_group)

        self.render_time_label = QLabel("0ms")
        metrics_layout.addRow("Last Render Time:", self.render_time_label)

        self.avatar_count_label = QLabel("0")
        metrics_layout.addRow("Active Avatars:", self.avatar_count_label)

        self.memory_usage_label = QLabel("0 KB")
        metrics_layout.addRow("Estimated Memory:", self.memory_usage_label)

        layout.addWidget(metrics_group)

        # Performance tests
        tests_group = QGroupBox("Performance Tests")
        tests_layout = QGridLayout(tests_group)

        # Mass creation test
        mass_create_btn = QPushButton("Create 50 Avatars")
        mass_create_btn.clicked.connect(self._test_mass_creation)
        tests_layout.addWidget(mass_create_btn, 0, 0)

        # Animation stress test
        anim_stress_btn = QPushButton("Animation Stress Test")
        anim_stress_btn.clicked.connect(self._test_animation_stress)
        tests_layout.addWidget(anim_stress_btn, 0, 1)

        # Memory test
        memory_test_btn = QPushButton("Memory Test")
        memory_test_btn.clicked.connect(self._test_memory_usage)
        tests_layout.addWidget(memory_test_btn, 1, 0)

        # Clean up test
        cleanup_btn = QPushButton("Clean Up All")
        cleanup_btn.clicked.connect(self._cleanup_all_avatars)
        tests_layout.addWidget(cleanup_btn, 1, 1)

        layout.addWidget(tests_group)

        # Animation playground
        playground_group = QGroupBox("Animation Playground")
        playground_layout = QVBoxLayout(playground_group)

        # Animation controls
        anim_controls_layout = QGridLayout()

        # Duration control
        anim_controls_layout.addWidget(QLabel("Duration:"), 0, 0)
        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setRange(100, 2000)
        self.duration_slider.setValue(300)
        anim_controls_layout.addWidget(self.duration_slider, 0, 1)

        self.duration_label = QLabel("300ms")
        self.duration_slider.valueChanged.connect(
            lambda v: self.duration_label.setText(f"{v}ms"))
        anim_controls_layout.addWidget(self.duration_label, 0, 2)

        # Easing control
        anim_controls_layout.addWidget(QLabel("Easing:"), 1, 0)
        self.easing_combo = QComboBox()
        self.easing_combo.addItems(
            ["Linear", "Ease In", "Ease Out", "Ease In Out", "Spring"])
        anim_controls_layout.addWidget(self.easing_combo, 1, 1, 1, 2)

        playground_layout.addLayout(anim_controls_layout)

        # Test avatar for playground
        self.playground_avatar = FluentAvatar(size=FluentAvatar.Size.XLARGE)
        self.playground_avatar.setName("Animation Test")
        playground_layout.addWidget(
            self.playground_avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Animation buttons
        anim_buttons_layout = QHBoxLayout()

        test_pulse_btn = QPushButton("Test Pulse")
        test_pulse_btn.clicked.connect(self._test_custom_pulse)
        anim_buttons_layout.addWidget(test_pulse_btn)

        test_scale_btn = QPushButton("Test Scale")
        test_scale_btn.clicked.connect(self._test_custom_scale)
        anim_buttons_layout.addWidget(test_scale_btn)

        test_fade_btn = QPushButton("Test Fade")
        test_fade_btn.clicked.connect(self._test_custom_fade)
        anim_buttons_layout.addWidget(test_fade_btn)

        playground_layout.addLayout(anim_buttons_layout)

        layout.addWidget(playground_group)

        # Performance monitor timer
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self._update_performance_metrics)
        self.perf_timer.start(1000)

        return widget

    # Event handlers for customization tab
    def _update_preview_size(self, index):
        """Update preview avatar size"""
        sizes = [FluentAvatar.Size.SMALL, FluentAvatar.Size.MEDIUM,
                 FluentAvatar.Size.LARGE, FluentAvatar.Size.XLARGE,
                 FluentAvatar.Size.XXLARGE]
        self.preview_avatar.setSize(sizes[index])

    def _update_preview_shape(self, index):
        """Update preview avatar shape"""
        shapes = [FluentAvatar.Shape.CIRCLE, FluentAvatar.Shape.ROUNDED_SQUARE,
                  FluentAvatar.Shape.SQUARE]
        self.preview_avatar.setShape(shapes[index])

    def _update_preview_name(self, name):
        """Update preview avatar name"""
        if name.strip():
            self.preview_avatar.setName(name)
        else:
            self.preview_avatar.setInitials("")

    def _update_preview_initials(self, initials):
        """Update preview avatar initials"""
        if initials:
            self.preview_avatar.setInitials(initials)
        else:
            # Revert to name-based initials
            self.preview_avatar.setName(self.name_input.text())

    def _update_preview_clickable(self, clickable):
        """Update preview avatar clickable state"""
        self.preview_avatar.setClickable(clickable)

    def _update_preview_border_width(self, width):
        """Update preview avatar border width"""
        self.preview_avatar.setBorderWidth(width)
        if width > 0:
            self.preview_avatar.setBorderColor(self.border_color)

    def _choose_border_color(self):
        """Choose border color"""
        color = QColorDialog.getColor(
            self.border_color, self, "Choose Border Color")
        if color.isValid():
            self.border_color = color
            self._update_border_color_button()
            if self.border_width_spin.value() > 0:
                self.preview_avatar.setBorderColor(color)

    def _update_border_color_button(self):
        """Update border color button appearance"""
        self.border_color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.border_color.name()};
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }}
        """)

    def _update_preview_auto_color(self, auto):
        """Update preview auto color setting"""
        self.bg_color_btn.setEnabled(not auto)
        if not auto:
            self.preview_avatar.setBackgroundColor(self.bg_color)
        else:
            self.preview_avatar.setBackgroundColor(QColor())

    def _choose_bg_color(self):
        """Choose background color"""
        color = QColorDialog.getColor(
            self.bg_color, self, "Choose Background Color")
        if color.isValid():
            self.bg_color = color
            if not self.auto_color_check.isChecked():
                self.preview_avatar.setBackgroundColor(color)

    def _load_photo(self):
        """Load photo for avatar"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Avatar Photo", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")

        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.preview_avatar.setPixmap(pixmap)
                self._log_event(f"Photo loaded: {os.path.basename(file_path)}")

    def _generate_demo_photo(self):
        """Generate a demo photo"""
        # Create a simple colored rectangle as demo photo
        pixmap = QPixmap(100, 100)
        pixmap.fill(QColor("#0078d4"))

        painter = QPainter(pixmap)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "DEMO")
        painter.end()

        self.preview_avatar.setPixmap(pixmap)
        self._log_event("Demo photo generated")

    def _clear_photo(self):
        """Clear avatar photo"""
        self.preview_avatar.setPixmap(QPixmap())
        self._log_event("Photo cleared")

    def _create_custom_avatar(self):
        """Create custom avatar and add to gallery"""
        # Clone current preview settings
        sizes = [FluentAvatar.Size.SMALL, FluentAvatar.Size.MEDIUM,
                 FluentAvatar.Size.LARGE, FluentAvatar.Size.XLARGE,
                 FluentAvatar.Size.XXLARGE]
        shapes = [FluentAvatar.Shape.CIRCLE, FluentAvatar.Shape.ROUNDED_SQUARE,
                  FluentAvatar.Shape.SQUARE]

        avatar = FluentAvatar(
            size=sizes[self.size_combo.currentIndex()],
            shape=shapes[self.shape_combo.currentIndex()]
        )

        # Copy settings
        if self.preview_avatar.pixmap():
            current_pixmap = self.preview_avatar.pixmap()
            if current_pixmap:
                avatar.setPixmap(current_pixmap)
        elif self.initials_input.text():
            avatar.setInitials(self.initials_input.text())
        else:
            avatar.setName(self.name_input.text())

        avatar.setClickable(self.clickable_check.isChecked())
        avatar.setBorderWidth(self.border_width_spin.value())

        if self.border_width_spin.value() > 0:
            avatar.setBorderColor(self.border_color)

        if not self.auto_color_check.isChecked():
            avatar.setBackgroundColor(self.bg_color)

        # Add to gallery
        self._add_to_gallery(avatar)
        self._log_event("Custom avatar created and added to gallery")

    def _add_to_gallery(self, avatar):
        """Add avatar to gallery"""
        # Create container for avatar
        container = QVBoxLayout()
        container.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add remove button
        remove_btn = QPushButton("Remove")
        remove_btn.setMaximumWidth(60)
        remove_btn.clicked.connect(
            lambda: self._remove_from_gallery(avatar, remove_btn))
        container.addWidget(remove_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add to grid
        row = len(self.demo_avatars) // 4
        col = len(self.demo_avatars) % 4

        self.gallery_layout.addLayout(container, row, col)
        self.demo_avatars.append(avatar)

        # Update count
        self.gallery_count_label.setText(f"{len(self.demo_avatars)} avatars")

    def _remove_from_gallery(self, avatar, button):
        """Remove avatar from gallery"""
        if avatar in self.demo_avatars:
            self.demo_avatars.remove(avatar)
            avatar.setParent(None)
            button.setParent(None)

            # Rebuild gallery layout
            self._rebuild_gallery()

            self._log_event("Avatar removed from gallery")

    def _rebuild_gallery(self):
        """Rebuild gallery layout"""
        # Clear layout
        for i in reversed(range(self.gallery_layout.count())):
            item = self.gallery_layout.itemAt(i)
            if item:
                self.gallery_layout.removeItem(item)

        # Re-add all avatars
        avatars_copy = self.demo_avatars.copy()
        self.demo_avatars.clear()

        for avatar in avatars_copy:
            self._add_to_gallery(avatar)

    def _clear_gallery(self):
        """Clear all avatars from gallery"""
        for avatar in self.demo_avatars:
            avatar.setParent(None)

        self.demo_avatars.clear()

        # Clear layout
        for i in reversed(range(self.gallery_layout.count())):
            item = self.gallery_layout.itemAt(i)
            if item:
                self.gallery_layout.removeItem(item)

        self.gallery_count_label.setText("0 avatars")
        self._log_event("Gallery cleared")

    def _reset_preview(self):
        """Reset preview to defaults"""
        self.size_combo.setCurrentIndex(2)
        self.shape_combo.setCurrentIndex(0)
        self.name_input.setText("Preview User")
        self.initials_input.clear()
        self.clickable_check.setChecked(True)
        self.border_width_spin.setValue(0)
        self.auto_color_check.setChecked(True)

        self.preview_avatar.setPixmap(QPixmap())
        self.preview_avatar.setName("Preview User")
        self._log_event("Preview reset to defaults")

    def _on_preview_clicked(self):
        """Handle preview avatar clicked"""
        self._log_event("Preview avatar clicked!")

    # Event handlers for groups tab
    def _create_sample_groups(self, layout):
        """Create sample avatar groups"""
        # Team group
        team_group = FluentAvatarGroup(max_visible=4)
        team_group.setSize(FluentAvatar.Size.MEDIUM)

        team_names = ["Alice Smith", "Bob Johnson",
                      "Carol Wilson", "David Brown", "Eve Davis"]
        for name in team_names:
            avatar = FluentAvatar()
            avatar.setName(name)
            team_group.addAvatar(avatar)

        team_container = QVBoxLayout()
        team_container.addWidget(QLabel("Team Group (4 visible):"))
        team_container.addWidget(team_group)
        layout.addLayout(team_container)

        # Store reference for management
        self.demo_group = team_group

        # Reviewers group
        reviewers_group = FluentAvatarGroup(max_visible=3)
        reviewers_group.setSize(FluentAvatar.Size.SMALL)

        reviewer_names = ["John Doe", "Jane Smith",
                          "Mike Chen", "Sarah Johnson", "Tom Wilson"]
        for name in reviewer_names:
            avatar = FluentAvatar()
            avatar.setName(name)
            reviewers_group.addAvatar(avatar)

        reviewers_container = QVBoxLayout()
        reviewers_container.addWidget(QLabel("Reviewers Group (3 visible):"))
        reviewers_container.addWidget(reviewers_group)
        layout.addLayout(reviewers_container)

        # Large group
        large_group = FluentAvatarGroup(max_visible=6)
        large_group.setSize(FluentAvatar.Size.LARGE)

        for i in range(10):
            avatar = FluentAvatar()
            avatar.setInitials(f"U{i+1}")
            large_group.addAvatar(avatar)

        large_container = QVBoxLayout()
        large_container.addWidget(QLabel("Large Group (6 visible):"))
        large_container.addWidget(large_group)
        layout.addLayout(large_container)

        # Store references
        self.avatar_groups = [team_group, reviewers_group, large_group]

    def _update_group_max_visible(self, value):
        """Update max visible for demo group"""
        if hasattr(self, 'demo_group'):
            self.demo_group.setMaxVisible(value)

    def _update_group_size(self, index):
        """Update group avatar size"""
        sizes = [FluentAvatar.Size.SMALL, FluentAvatar.Size.MEDIUM,
                 FluentAvatar.Size.LARGE, FluentAvatar.Size.XLARGE,
                 FluentAvatar.Size.XXLARGE]

        if hasattr(self, 'demo_group'):
            self.demo_group.setSize(sizes[index])

    def _update_group_overlap(self, value):
        """Update group overlap"""
        if hasattr(self, 'demo_group'):
            self.demo_group.setOverlap(value)

    def _add_random_avatar_to_group(self):
        """Add random avatar to demo group"""
        if hasattr(self, 'demo_group'):
            import random
            names = ["Alex Johnson", "Sam Wilson", "Jordan Brown", "Casey Davis",
                     "Taylor Miller", "Morgan White", "Jamie Garcia", "Riley Martinez"]

            avatar = FluentAvatar()
            avatar.setName(random.choice(names))
            self.demo_group.addAvatar(avatar)

            self._log_event("Random avatar added to group")

    def _remove_last_avatar_from_group(self):
        """Remove last avatar from demo group"""
        if hasattr(self, 'demo_group') and self.demo_group._avatars:
            last_avatar = self.demo_group._avatars[-1]
            self.demo_group.removeAvatar(last_avatar)
            self._log_event("Last avatar removed from group")

    def _clear_demo_group(self):
        """Clear demo group"""
        if hasattr(self, 'demo_group'):
            self.demo_group.clear()
            self._log_event("Demo group cleared")

    def _create_new_demo_group(self):
        """Create new demo group"""
        new_group = FluentAvatarGroup(max_visible=5)

        # Add some initial avatars
        for i in range(3):
            avatar = FluentAvatar()
            avatar.setInitials(f"N{i+1}")
            new_group.addAvatar(avatar)

        # Replace demo group
        self.demo_group = new_group
        self._log_event("New demo group created")

    def _populate_with_team(self):
        """Populate group with full team"""
        if hasattr(self, 'demo_group'):
            self.demo_group.clear()

            team = [
                "Alice Cooper", "Bob Smith", "Carol Johnson", "David Wilson",
                "Eve Brown", "Frank Davis", "Grace Miller", "Henry Taylor",
                "Ivy Anderson", "Jack Thompson"
            ]

            for name in team:
                avatar = FluentAvatar()
                avatar.setName(name)
                self.demo_group.addAvatar(avatar)

            self._log_event("Group populated with full team")

    def _stress_test_group(self):
        """Stress test with many avatars"""
        if hasattr(self, 'demo_group'):
            self.demo_group.clear()

            for i in range(20):
                avatar = FluentAvatar()
                avatar.setInitials(f"T{i+1}")
                self.demo_group.addAvatar(avatar)

            self._log_event("Stress test: 20 avatars added")

    # Event handlers for interactive tab
    def _show_profile_action(self):
        """Show profile action"""
        self._log_event("Profile avatar clicked - Opening profile...")

    def _show_settings_action(self):
        """Show settings action"""
        self._log_event("Settings avatar clicked - Opening settings...")

    def _show_messages_action(self):
        """Show messages action"""
        self._log_event("Messages avatar clicked - Opening messages...")

    def _show_notifications_action(self):
        """Show notifications action"""
        self._log_event(
            "Notifications avatar clicked - Opening notifications...")

    def _create_animation_targets(self):
        """Create avatars for animation testing"""
        self.animation_avatars = []

        for i in range(3):
            avatar = FluentAvatar(size=FluentAvatar.Size.LARGE)
            avatar.setName(f"Anim {i+1}")
            self.animation_targets_layout.addWidget(avatar)
            self.animation_avatars.append(avatar)

    def _demo_pulse_animation(self):
        """Demo pulse animation"""
        for avatar in self.animation_avatars:
            # This would use the micro-interaction system
            pass
        self._log_event("Pulse animation demonstrated")

    def _demo_scale_animation(self):
        """Demo scale animation"""
        for avatar in self.animation_avatars:
            # This would use the micro-interaction system
            pass
        self._log_event("Scale animation demonstrated")

    def _demo_fade_animation(self):
        """Demo fade animation"""
        for avatar in self.animation_avatars:
            # This would use the reveal effect system
            pass
        self._log_event("Fade animation demonstrated")

    def _demo_name_change(self):
        """Demo name change"""
        import random
        names = ["John Smith", "Jane Doe",
                 "Alice Cooper", "Bob Wilson", "Carol Davis"]
        new_name = random.choice(names)
        self.state_demo_avatar.setName(new_name)
        self._log_event(f"Name changed to: {new_name}")

    def _demo_initials_change(self):
        """Demo initials change"""
        import random
        initials = ["AB", "CD", "EF", "GH", "IJ", "KL"]
        new_initials = random.choice(initials)
        self.state_demo_avatar.setInitials(new_initials)
        self._log_event(f"Initials changed to: {new_initials}")

    def _demo_size_change(self):
        """Demo size change"""
        import random
        sizes = [FluentAvatar.Size.SMALL, FluentAvatar.Size.MEDIUM,
                 FluentAvatar.Size.LARGE, FluentAvatar.Size.XLARGE]
        new_size = random.choice(sizes)
        self.state_demo_avatar.setSize(new_size)
        self._log_event(f"Size changed to: {new_size.value}px")

    def _demo_shape_change(self):
        """Demo shape change"""
        import random
        shapes = [FluentAvatar.Shape.CIRCLE, FluentAvatar.Shape.ROUNDED_SQUARE,
                  FluentAvatar.Shape.SQUARE]
        new_shape = random.choice(shapes)
        self.state_demo_avatar.setShape(new_shape)
        self._log_event(f"Shape changed to: {new_shape.value}")

    def _demo_border_toggle(self):
        """Demo border toggle"""
        current_width = self.state_demo_avatar.borderWidth()
        new_width = 0 if current_width > 0 else 2
        self.state_demo_avatar.setBorderWidth(new_width)

        if new_width > 0:
            self.state_demo_avatar.setBorderColor(QColor("#0078d4"))

        self._log_event(f"Border {'enabled' if new_width > 0 else 'disabled'}")

    def _demo_color_change(self):
        """Demo color change"""
        import random
        colors = [QColor("#0078d4"), QColor("#107c10"), QColor("#d13438"),
                  QColor("#ff8c00"), QColor("#5c2d91")]
        new_color = random.choice(colors)
        self.state_demo_avatar.setBackgroundColor(new_color)
        self._log_event(f"Background color changed to: {new_color.name()}")

    # Event handlers for gallery tab
    def _show_member_details(self, name, role):
        """Show member details"""
        self._log_event(f"Team member clicked: {name} ({role})")

    # Event handlers for performance tab
    def _update_performance_metrics(self):
        """Update performance metrics"""
        total_avatars = len(self.demo_avatars) + sum(len(group._avatars)
                                                     for group in self.avatar_groups)
        self.avatar_count_label.setText(str(total_avatars))

        # Estimate memory usage (rough calculation)
        estimated_memory = total_avatars * 10  # 10KB per avatar estimate
        self.memory_usage_label.setText(f"{estimated_memory} KB")

    def _test_mass_creation(self):
        """Test mass avatar creation"""
        start_time = QElapsedTimer()
        start_time.start()

        for i in range(50):
            avatar = FluentAvatar()
            avatar.setName(f"Test User {i+1}")
            self._add_to_gallery(avatar)

        elapsed = start_time.elapsed()
        self.render_time_label.setText(f"{elapsed}ms")
        self._log_event(
            f"Mass creation test: 50 avatars created in {elapsed}ms")

    def _test_animation_stress(self):
        """Test animation stress"""
        for avatar in self.demo_avatars[-10:]:  # Animate last 10 avatars
            # Apply multiple animations
            pass

        self._log_event("Animation stress test completed")

    def _test_memory_usage(self):
        """Test memory usage"""
        import sys
        memory_before = sys.getsizeof(self.demo_avatars)

        # Create temporary avatars
        temp_avatars = []
        for i in range(100):
            avatar = FluentAvatar()
            avatar.setName(f"Temp {i}")
            temp_avatars.append(avatar)

        memory_after = sys.getsizeof(temp_avatars)
        memory_diff = memory_after - memory_before

        # Clean up
        temp_avatars.clear()

        self._log_event(f"Memory test: {memory_diff} bytes for 100 avatars")

    def _cleanup_all_avatars(self):
        """Clean up all avatars"""
        self._clear_gallery()

        for group in self.avatar_groups:
            group.clear()

        self._log_event("All avatars cleaned up")

    def _test_custom_pulse(self):
        """Test custom pulse animation"""
        duration = self.duration_slider.value()
        self._log_event(f"Custom pulse animation: {duration}ms duration")

    def _test_custom_scale(self):
        """Test custom scale animation"""
        duration = self.duration_slider.value()
        self._log_event(f"Custom scale animation: {duration}ms duration")

    def _test_custom_fade(self):
        """Test custom fade animation"""
        duration = self.duration_slider.value()
        self._log_event(f"Custom fade animation: {duration}ms duration")

    def _log_event(self, event):
        """Log event to event log"""
        if hasattr(self, 'event_log'):
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.event_log.append(f"[{timestamp}] {event}")


class AvatarExampleWindow(QMainWindow):
    """Main window for avatar examples"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FluentAvatar Components - Complete Demo")
        self.setGeometry(100, 100, 1400, 900)

        # Create central widget
        central_widget = AvatarDemoWidget()
        self.setCentralWidget(central_widget)

        # Apply theme
        # theme_manager.apply_theme_to_widget(self)

        # Status bar
        self.statusBar().showMessage("Ready - Explore all avatar features and customizations")


def main():
    """Run the avatar example application"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("FluentAvatar Demo")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Fluent Widget Examples")

    # Create and show window
    window = AvatarExampleWindow()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
