"""
Comprehensive Media Controls Demo

This demo showcases all media control components available in the simple-fluent-widget library,
including audio/video players, media browsers, and playback controls.

Features demonstrated:
- Audio player with playlist support
- Video player with controls overlay
- Media browser and file management
- Volume and playback controls
- Streaming and local media support
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox,
    QScrollArea, QFrame, QSpacerItem, QSizePolicy, QMessageBox, QTabWidget,
    QSlider, QSpinBox, QCheckBox, QComboBox, QProgressBar, QListWidget,
    QListWidgetItem, QFileDialog, QSplitter, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QUrl
from PySide6.QtGui import QColor, QPalette, QFont, QIcon, QPixmap
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

# Import fluent media components with fallbacks
try:
    from components.controls.media.players import (
        FluentAudioPlayer, FluentVideoPlayer, FluentMediaBrowser
    )
    FLUENT_MEDIA_AVAILABLE = True
except ImportError:
    print("Warning: Fluent media components not available")
    FLUENT_MEDIA_AVAILABLE = False

try:
    from components.layout.containers import FluentCard
    FLUENT_CARD_AVAILABLE = True
except ImportError:
    FLUENT_CARD_AVAILABLE = False


class MediaPlayerWidget(QWidget):
    """Custom media player widget with Fluent design."""
    
    def __init__(self, media_type="audio"):
        super().__init__()
        self.media_type = media_type
        self.current_file = None
        self.playlist = []
        self.current_index = 0
        
        self.setup_ui()
        self.setup_media_player()
        
    def setup_ui(self):
        """Set up the media player UI."""
        layout = QVBoxLayout(self)
        
        # Media display area
        if self.media_type == "video":
            self.video_widget = QVideoWidget()
            self.video_widget.setMinimumHeight(300)
            layout.addWidget(self.video_widget)
        else:
            # Audio visualization placeholder
            audio_display = QFrame()
            audio_display.setMinimumHeight(200)
            audio_display.setStyleSheet("""
                QFrame {
                    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
                    border-radius: 8px;
                    border: 1px solid #c8c6c4;
                }
            """)
            
            display_layout = QVBoxLayout(audio_display)
            self.audio_title = QLabel("No media loaded")
            self.audio_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.audio_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
            display_layout.addWidget(self.audio_title)
            
            self.audio_artist = QLabel("")
            self.audio_artist.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.audio_artist.setStyleSheet("color: #f0f0f0; font-size: 14px;")
            display_layout.addWidget(self.audio_artist)
            
            layout.addWidget(audio_display)
        
        # Progress bar
        self.progress_bar = QSlider(Qt.Orientation.Horizontal)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.sliderPressed.connect(self.on_progress_pressed)
        self.progress_bar.sliderReleased.connect(self.on_progress_released)
        layout.addWidget(self.progress_bar)
        
        # Time labels
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time_label)
        layout.addLayout(time_layout)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.clicked.connect(self.previous_track)
        controls_layout.addWidget(self.prev_btn)
        
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        controls_layout.addWidget(self.play_pause_btn)
        
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_btn)
        
        self.next_btn = QPushButton("⏭")
        self.next_btn.clicked.connect(self.next_track)
        controls_layout.addWidget(self.next_btn)
        
        # Volume control
        controls_layout.addWidget(QLabel("🔊"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        controls_layout.addWidget(self.volume_slider)
        
        layout.addLayout(controls_layout)
        
        # Apply Fluent styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #f3f2f1;
                border: 1px solid #c8c6c4;
                border-radius: 4px;
                padding: 8px;
                min-width: 40px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e1dfdd;
            }
            QPushButton:pressed {
                background-color: #d2d0ce;
            }
            QSlider::groove:horizontal {
                border: 1px solid #c8c6c4;
                height: 4px;
                background: #f3f2f1;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #005a9e;
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #106ebe;
            }
        """)
        
    def setup_media_player(self):
        """Set up the media player backend."""
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        
        self.media_player.setAudioOutput(self.audio_output)
        
        if self.media_type == "video" and hasattr(self, 'video_widget'):
            self.media_player.setVideoOutput(self.video_widget)
        
        # Connect signals
        self.media_player.positionChanged.connect(self.on_position_changed)
        self.media_player.durationChanged.connect(self.on_duration_changed)
        self.media_player.playbackStateChanged.connect(self.on_playback_state_changed)
        
        # Set initial volume
        self.audio_output.setVolume(0.7)
        
    def load_file(self, file_path):
        """Load a media file."""
        self.current_file = file_path
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        
        # Update display
        file_name = os.path.basename(file_path)
        if self.media_type == "audio":
            self.audio_title.setText(file_name)
            # In a real implementation, you'd extract metadata
            self.audio_artist.setText("Unknown Artist")
        
    def toggle_play_pause(self):
        """Toggle play/pause state."""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
            
    def stop_playback(self):
        """Stop playback."""
        self.media_player.stop()
        
    def previous_track(self):
        """Play previous track in playlist."""
        if self.playlist and self.current_index > 0:
            self.current_index -= 1
            self.load_file(self.playlist[self.current_index])
            self.media_player.play()
            
    def next_track(self):
        """Play next track in playlist."""
        if self.playlist and self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.load_file(self.playlist[self.current_index])
            self.media_player.play()
            
    def set_volume(self, value):
        """Set playback volume."""
        self.audio_output.setVolume(value / 100.0)
        
    def set_playlist(self, files):
        """Set the playlist."""
        self.playlist = files
        self.current_index = 0
        if files:
            self.load_file(files[0])
            
    def on_position_changed(self, position):
        """Handle position change."""
        if not self.progress_bar.isSliderDown():
            duration = self.media_player.duration()
            if duration > 0:
                self.progress_bar.setValue(int(position * 100 / duration))
        
        # Update time display
        self.current_time_label.setText(self.format_time(position))
        
    def on_duration_changed(self, duration):
        """Handle duration change."""
        self.total_time_label.setText(self.format_time(duration))
        
    def on_playback_state_changed(self, state):
        """Handle playback state change."""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_pause_btn.setText("⏸")
        else:
            self.play_pause_btn.setText("▶")
            
    def on_progress_pressed(self):
        """Handle progress bar press."""
        pass
        
    def on_progress_released(self):
        """Handle progress bar release."""
        duration = self.media_player.duration()
        if duration > 0:
            position = int(self.progress_bar.value() * duration / 100)
            self.media_player.setPosition(position)
            
    def format_time(self, milliseconds):
        """Format time in milliseconds to MM:SS format."""
        seconds = int(milliseconds / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"


class PlaylistWidget(QWidget):
    """Playlist management widget."""
    
    file_selected = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the playlist UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Playlist"))
        
        add_btn = QPushButton("Add Files")
        add_btn.clicked.connect(self.add_files)
        header_layout.addWidget(add_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_playlist)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Playlist
        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.playlist_widget)
        
    def add_files(self):
        """Add files to playlist."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Add Media Files", "",
            "Media Files (*.mp3 *.mp4 *.avi *.wav *.m4a *.flac);;All Files (*)"
        )
        
        for file_path in files:
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.playlist_widget.addItem(item)
            
    def clear_playlist(self):
        """Clear the playlist."""
        self.playlist_widget.clear()
        
    def on_item_double_clicked(self, item):
        """Handle item double click."""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        self.file_selected.emit(file_path)
        
    def get_all_files(self):
        """Get all files in playlist."""
        files = []
        for i in range(self.playlist_widget.count()):
            item = self.playlist_widget.item(i)
            files.append(item.data(Qt.ItemDataRole.UserRole))
        return files


class MediaControlsDemo(QMainWindow):
    """Main demo window showcasing media control components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Controls Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Media Controls Demo")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Tab widget for different media types
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create demo tabs
        self.create_audio_player_tab()
        self.create_video_player_tab()
        self.create_media_browser_tab()
        self.create_streaming_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready - Load media files to begin playback")
        
    def create_audio_player_tab(self):
        """Create audio player demonstration tab."""
        tab_widget = QWidget()
        layout = QHBoxLayout(tab_widget)
        
        # Main player area
        player_group = QGroupBox("Audio Player")
        player_layout = QVBoxLayout(player_group)
        
        # Audio player widget
        self.audio_player = MediaPlayerWidget("audio")
        player_layout.addWidget(self.audio_player)
        
        # Player controls
        controls_group = QGroupBox("Player Controls")
        controls_layout = QGridLayout(controls_group)
        
        # Equalizer simulation
        eq_label = QLabel("Equalizer (Simulation):")
        controls_layout.addWidget(eq_label, 0, 0, 1, 2)
        
        eq_bands = ["60Hz", "170Hz", "310Hz", "600Hz", "1kHz", "3kHz", "6kHz", "12kHz"]
        self.eq_sliders = []
        
        for i, band in enumerate(eq_bands):
            band_layout = QVBoxLayout()
            
            slider = QSlider(Qt.Orientation.Vertical)
            slider.setRange(-12, 12)
            slider.setValue(0)
            slider.setMaximumHeight(100)
            self.eq_sliders.append(slider)
            
            band_layout.addWidget(slider)
            band_layout.addWidget(QLabel(band))
            
            controls_layout.addLayout(band_layout, 1, i)
            
        # Playback options
        options_layout = QVBoxLayout()
        
        self.repeat_check = QCheckBox("Repeat")
        options_layout.addWidget(self.repeat_check)
        
        self.shuffle_check = QCheckBox("Shuffle")
        options_layout.addWidget(self.shuffle_check)
        
        self.crossfade_check = QCheckBox("Crossfade")
        options_layout.addWidget(self.crossfade_check)
        
        controls_layout.addLayout(options_layout, 2, 0, 1, 8)
        
        player_layout.addWidget(controls_group)
        
        layout.addWidget(player_group)
        
        # Playlist sidebar
        self.audio_playlist = PlaylistWidget()
        self.audio_playlist.file_selected.connect(self.load_audio_file)
        layout.addWidget(self.audio_playlist)
        
        self.tab_widget.addTab(tab_widget, "Audio Player")
        
    def create_video_player_tab(self):
        """Create video player demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Video player area
        player_group = QGroupBox("Video Player")
        player_layout = QVBoxLayout(player_group)
        
        # Video player widget
        self.video_player = MediaPlayerWidget("video")
        player_layout.addWidget(self.video_player)
        
        # Video controls
        video_controls_group = QGroupBox("Video Controls")
        video_controls_layout = QHBoxLayout(video_controls_group)
        
        # Load video button
        load_video_btn = QPushButton("Load Video")
        load_video_btn.clicked.connect(self.load_video_file)
        video_controls_layout.addWidget(load_video_btn)
        
        # Playback speed
        video_controls_layout.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentText("1.0x")
        self.speed_combo.currentTextChanged.connect(self.change_playback_speed)
        video_controls_layout.addWidget(self.speed_combo)
        
        # Aspect ratio
        video_controls_layout.addWidget(QLabel("Aspect:"))
        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems(["Auto", "4:3", "16:9", "16:10"])
        video_controls_layout.addWidget(self.aspect_combo)
        
        # Fullscreen
        fullscreen_btn = QPushButton("Fullscreen")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        video_controls_layout.addWidget(fullscreen_btn)
        
        video_controls_layout.addStretch()
        
        player_layout.addWidget(video_controls_group)
        
        layout.addWidget(player_group)
        
        self.tab_widget.addTab(tab_widget, "Video Player")
        
    def create_media_browser_tab(self):
        """Create media browser demonstration tab."""
        tab_widget = QWidget()
        layout = QHBoxLayout(tab_widget)
        
        # File browser
        browser_group = QGroupBox("Media Browser")
        browser_layout = QVBoxLayout(browser_group)
        
        # Browser controls
        browser_controls = QHBoxLayout()
        
        browse_btn = QPushButton("Browse Folder")
        browse_btn.clicked.connect(self.browse_media_folder)
        browser_controls.addWidget(browse_btn)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Media", "Audio Only", "Video Only"])
        self.filter_combo.currentTextChanged.connect(self.filter_media)
        browser_controls.addWidget(self.filter_combo)
        
        browser_controls.addStretch()
        
        browser_layout.addLayout(browser_controls)
        
        # File tree
        self.media_tree = QTreeWidget()
        self.media_tree.setHeaderLabels(["Name", "Type", "Size", "Duration"])
        self.media_tree.itemDoubleClicked.connect(self.play_selected_media)
        browser_layout.addWidget(self.media_tree)
        
        layout.addWidget(browser_group)
        
        # Media info panel
        info_group = QGroupBox("Media Information")
        info_layout = QVBoxLayout(info_group)
        
        self.media_info_display = QTextEdit()
        self.media_info_display.setReadOnly(True)
        self.media_info_display.setMaximumWidth(300)
        info_layout.addWidget(self.media_info_display)
        
        # Quick actions
        actions_layout = QVBoxLayout()
        
        play_btn = QPushButton("Play Selected")
        play_btn.clicked.connect(self.play_selected_media)
        actions_layout.addWidget(play_btn)
        
        add_to_playlist_btn = QPushButton("Add to Playlist")
        add_to_playlist_btn.clicked.connect(self.add_to_playlist)
        actions_layout.addWidget(add_to_playlist_btn)
        
        actions_layout.addStretch()
        
        info_layout.addLayout(actions_layout)
        
        layout.addWidget(info_group)
        
        self.tab_widget.addTab(tab_widget, "Media Browser")
        
    def create_streaming_tab(self):
        """Create streaming demonstration tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Streaming controls
        streaming_group = QGroupBox("Streaming Controls")
        streaming_layout = QVBoxLayout(streaming_group)
        
        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Stream URL:"))
        
        self.stream_url_input = QLineEdit()
        self.stream_url_input.setPlaceholderText("Enter streaming URL (http://, rtsp://, etc.)")
        url_layout.addWidget(self.stream_url_input)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_to_stream)
        url_layout.addWidget(connect_btn)
        
        streaming_layout.addLayout(url_layout)
        
        # Streaming status
        self.stream_status = QLabel("Not connected")
        self.stream_status.setStyleSheet("color: #d13438; font-weight: bold;")
        streaming_layout.addWidget(self.stream_status)
        
        # Stream info
        stream_info_layout = QGridLayout()
        
        stream_info_layout.addWidget(QLabel("Bitrate:"), 0, 0)
        self.bitrate_label = QLabel("--")
        stream_info_layout.addWidget(self.bitrate_label, 0, 1)
        
        stream_info_layout.addWidget(QLabel("Format:"), 1, 0)
        self.format_label = QLabel("--")
        stream_info_layout.addWidget(self.format_label, 1, 1)
        
        stream_info_layout.addWidget(QLabel("Buffer:"), 2, 0)
        self.buffer_progress = QProgressBar()
        stream_info_layout.addWidget(self.buffer_progress, 2, 1)
        
        streaming_layout.addLayout(stream_info_layout)
        
        layout.addWidget(streaming_group)
        
        # Stream player
        stream_player_group = QGroupBox("Stream Player")
        stream_player_layout = QVBoxLayout(stream_player_group)
        
        self.stream_player = MediaPlayerWidget("video")
        stream_player_layout.addWidget(self.stream_player)
        
        layout.addWidget(stream_player_group)
        
        # Documentation
        docs_group = QGroupBox("Streaming Features")
        docs_layout = QVBoxLayout(docs_group)
        
        docs_text = QLabel("""
<b>Streaming Capabilities:</b><br>
• <b>Multiple Protocols:</b> HTTP, RTSP, RTMP, UDP streams<br>
• <b>Adaptive Bitrate:</b> Automatic quality adjustment<br>
• <b>Buffering Control:</b> Configurable buffer sizes<br>
• <b>Network Resilience:</b> Automatic reconnection<br>
• <b>Live Streams:</b> Real-time streaming support<br><br>

<b>Supported Formats:</b><br>
• Audio: MP3, AAC, FLAC, OGG, WAV<br>
• Video: MP4, AVI, MKV, MOV, WebM<br>
• Streaming: HLS, DASH, RTMP, RTSP<br>
""")
        docs_text.setWordWrap(True)
        docs_layout.addWidget(docs_text)
        
        layout.addWidget(docs_group)
        
        self.tab_widget.addTab(tab_widget, "Streaming")
        
    # Event handlers
    def load_audio_file(self, file_path):
        """Load an audio file in the audio player."""
        self.audio_player.load_file(file_path)
        self.audio_player.set_playlist(self.audio_playlist.get_all_files())
        self.statusBar().showMessage(f"Loaded: {os.path.basename(file_path)}")
        
    def load_video_file(self):
        """Load a video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv);;All Files (*)"
        )
        
        if file_path:
            self.video_player.load_file(file_path)
            self.statusBar().showMessage(f"Loaded video: {os.path.basename(file_path)}")
            
    def change_playback_speed(self, speed_text):
        """Change video playback speed."""
        speed = float(speed_text.replace('x', ''))
        self.video_player.media_player.setPlaybackRate(speed)
        self.statusBar().showMessage(f"Playback speed: {speed_text}")
        
    def toggle_fullscreen(self):
        """Toggle video fullscreen mode."""
        if hasattr(self.video_player, 'video_widget'):
            if self.video_player.video_widget.isFullScreen():
                self.video_player.video_widget.showNormal()
            else:
                self.video_player.video_widget.showFullScreen()
                
    def browse_media_folder(self):
        """Browse for media folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Media Folder")
        
        if folder:
            self.populate_media_tree(folder)
            self.statusBar().showMessage(f"Browsing: {folder}")
            
    def populate_media_tree(self, folder_path):
        """Populate the media tree with files."""
        self.media_tree.clear()
        
        media_extensions = {
            '.mp3', '.mp4', '.avi', '.wav', '.m4a', '.flac', 
            '.mkv', '.mov', '.wmv', '.ogg', '.webm'
        }
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in media_extensions):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, folder_path)
                    
                    # Determine media type
                    ext = os.path.splitext(file)[1].lower()
                    if ext in {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}:
                        media_type = "Audio"
                    else:
                        media_type = "Video"
                    
                    # Get file size
                    try:
                        size = os.path.getsize(file_path)
                        size_str = self.format_file_size(size)
                    except:
                        size_str = "Unknown"
                    
                    # Create tree item
                    item = QTreeWidgetItem([file, media_type, size_str, "--"])
                    item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                    self.media_tree.addTopLevelItem(item)
                    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
        
    def filter_media(self, filter_type):
        """Filter media by type."""
        for i in range(self.media_tree.topLevelItemCount()):
            item = self.media_tree.topLevelItem(i)
            media_type = item.text(1)
            
            if filter_type == "All Media":
                item.setHidden(False)
            elif filter_type == "Audio Only":
                item.setHidden(media_type != "Audio")
            elif filter_type == "Video Only":
                item.setHidden(media_type != "Video")
                
    def play_selected_media(self):
        """Play the selected media file."""
        current_item = self.media_tree.currentItem()
        if current_item:
            file_path = current_item.data(0, Qt.ItemDataRole.UserRole)
            media_type = current_item.text(1)
            
            if media_type == "Audio":
                self.audio_player.load_file(file_path)
                self.tab_widget.setCurrentIndex(0)  # Switch to audio tab
            else:
                self.video_player.load_file(file_path)
                self.tab_widget.setCurrentIndex(1)  # Switch to video tab
                
            self.update_media_info(file_path, current_item)
            
    def update_media_info(self, file_path, item):
        """Update media information display."""
        info = f"""
<b>File:</b> {os.path.basename(file_path)}<br>
<b>Path:</b> {file_path}<br>
<b>Type:</b> {item.text(1)}<br>
<b>Size:</b> {item.text(2)}<br>
<b>Modified:</b> {datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')}<br><br>

<b>Technical Details:</b><br>
<i>Codec information would be displayed here in a full implementation.</i>
"""
        self.media_info_display.setHtml(info)
        
    def add_to_playlist(self):
        """Add selected media to playlist."""
        current_item = self.media_tree.currentItem()
        if current_item:
            file_path = current_item.data(0, Qt.ItemDataRole.UserRole)
            
            # Add to appropriate playlist
            media_type = current_item.text(1)
            if media_type == "Audio":
                item = QListWidgetItem(os.path.basename(file_path))
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.audio_playlist.playlist_widget.addItem(item)
                self.statusBar().showMessage(f"Added to audio playlist: {os.path.basename(file_path)}")
                
    def connect_to_stream(self):
        """Connect to streaming URL."""
        url = self.stream_url_input.text().strip()
        if url:
            self.stream_player.media_player.setSource(QUrl(url))
            self.stream_status.setText("Connecting...")
            self.stream_status.setStyleSheet("color: #f5a623; font-weight: bold;")
            
            # Simulate connection (in real implementation, this would be handled by media player events)
            QTimer.singleShot(2000, self.simulate_stream_connected)
            
            self.statusBar().showMessage(f"Connecting to stream: {url}")
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid stream URL")
            
    def simulate_stream_connected(self):
        """Simulate successful stream connection."""
        self.stream_status.setText("Connected")
        self.stream_status.setStyleSheet("color: #107c10; font-weight: bold;")
        self.bitrate_label.setText("256 kbps")
        self.format_label.setText("H.264/AAC")
        self.buffer_progress.setValue(85)


def main():
    """Main function to run the demo."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Media Controls Demo")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Simple Fluent Widget")
    
    # Create and show the demo
    demo = MediaControlsDemo()
    demo.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
