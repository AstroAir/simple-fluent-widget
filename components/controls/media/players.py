"""
Fluent Design Media and Rich Content Components
Media players, image viewers, and rich content display components
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QSlider, QProgressBar, QFrame, QScrollArea, QTextEdit,
                               QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                               QSizePolicy, QFileDialog, QApplication, QMenu, QGridLayout)
from PySide6.QtCore import (Qt, Signal, QTimer, QUrl, QSize, QRect, QPoint,
                           QPropertyAnimation, QEasingCurve, QThread)
from PySide6.QtGui import (QPainter, QColor, QFont, QPen, QBrush, QPixmap, QIcon,
                          QMovie, QFontMetrics, QPainterPath, QTransform, 
                          QWheelEvent, QMouseEvent, QPaintEvent)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional, List, Dict, Any, Tuple
import os
import mimetypes
import time


class FluentImageViewer(QWidget):
    """Fluent Design style image viewer with zoom and pan"""
    
    image_changed = Signal(str)  # file_path
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._current_image = None
        self._zoom_factor = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 5.0
        self._pan_offset = QPoint(0, 0)
        self._last_pan_point = QPoint(0, 0)
        self._is_panning = False
        
        self._setup_ui()
        self._setup_style()
        
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(48)
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(8)
        
        # Open button
        self.open_btn = QPushButton("Open Image")
        self.open_btn.clicked.connect(self._open_image)
        
        # Zoom controls
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setFixedSize(32, 32)
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        
        self.zoom_reset_btn = QPushButton("100%")
        self.zoom_reset_btn.setFixedWidth(60)
        self.zoom_reset_btn.clicked.connect(self._zoom_reset)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedSize(32, 32)
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        
        # Fit to window button
        self.fit_btn = QPushButton("Fit")
        self.fit_btn.clicked.connect(self._fit_to_window)
        
        toolbar_layout.addWidget(self.open_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.zoom_out_btn)
        toolbar_layout.addWidget(self.zoom_reset_btn)
        toolbar_layout.addWidget(self.zoom_in_btn)
        toolbar_layout.addWidget(self.fit_btn)
        
        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setText("No image loaded")
        self.image_label.setStyleSheet("border: 2px dashed #cccccc; color: #888888;")
        
        # Scroll area for panning
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.scroll_area, 1)
    
    def loadImage(self, file_path: str):
        """Load image from file"""
        if os.path.exists(file_path):
            self._current_image = QPixmap(file_path)
            if not self._current_image.isNull():
                self._display_image()
                self.image_changed.emit(file_path)
            else:
                self.image_label.setText("Failed to load image")
    
    def _open_image(self):
        """Open image file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.ico)"
        )
        if file_path:
            self.loadImage(file_path)
    
    def _display_image(self):
        """Display current image with zoom"""
        if self._current_image:
            scaled_pixmap = self._current_image.scaled(
                self._current_image.size() * self._zoom_factor,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.resize(scaled_pixmap.size())
            self._update_zoom_label()
    
    def _zoom_in(self):
        """Zoom in"""
        if self._zoom_factor < self._max_zoom:
            self._zoom_factor = min(self._zoom_factor * 1.25, self._max_zoom)
            self._display_image()
    
    def _zoom_out(self):
        """Zoom out"""
        if self._zoom_factor > self._min_zoom:
            self._zoom_factor = max(self._zoom_factor / 1.25, self._min_zoom)
            self._display_image()
    
    def _zoom_reset(self):
        """Reset zoom to 100%"""
        self._zoom_factor = 1.0
        self._display_image()
    
    def _fit_to_window(self):
        """Fit image to window"""
        if self._current_image:
            available_size = self.scroll_area.size()
            image_size = self._current_image.size()
            
            scale_x = available_size.width() / image_size.width()
            scale_y = available_size.height() / image_size.height()
            self._zoom_factor = min(scale_x, scale_y) * 0.95  # 5% margin
            
            self._display_image()
    
    def _update_zoom_label(self):
        """Update zoom percentage label"""
        percentage = int(self._zoom_factor * 100)
        self.zoom_reset_btn.setText(f"{percentage}%")
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel zoom"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self._zoom_in()
            else:
                self._zoom_out()
        else:
            super().wheelEvent(event)
    
    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        
        style_sheet = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QPushButton {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('primary').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QScrollArea {{
                background-color: {theme.get_color('background').name()};
                border: none;
            }}
        """
        
        self.setStyleSheet(style_sheet)
    
    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentMediaPlayer(QWidget):
    """Fluent Design style media player"""
    
    position_changed = Signal(int)  # position in ms
    duration_changed = Signal(int)  # duration in ms
    playing_changed = Signal(bool)  # is playing
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._duration = 0
        self._position = 0
        self._is_playing = False
        self._volume = 50
        
        self._setup_ui()
        self._setup_media_player()
        self._setup_style()
        
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(300)
        
        # Controls
        self.controls = QFrame()
        self.controls.setFixedHeight(80)
        controls_layout = QVBoxLayout(self.controls)
        controls_layout.setContentsMargins(16, 8, 16, 8)
        controls_layout.setSpacing(8)
        
        # Progress bar
        self.progress_bar = QSlider(Qt.Orientation.Horizontal)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(1000)
        self.progress_bar.valueChanged.connect(self._seek_position)
        
        # Control buttons row
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        # Play/Pause button
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(40, 40)
        self.play_btn.clicked.connect(self._toggle_play_pause)
        
        # Stop button
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setFixedSize(40, 40)
        self.stop_btn.clicked.connect(self._stop)
        
        # Time labels
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(100)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(4)
        
        self.volume_btn = QPushButton("🔊")
        self.volume_btn.setFixedSize(32, 32)
        self.volume_btn.clicked.connect(self._toggle_mute)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self._volume)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self._set_volume)
        
        volume_layout.addWidget(self.volume_btn)
        volume_layout.addWidget(self.volume_slider)
        
        # Open file button
        self.open_btn = QPushButton("Open Media")
        self.open_btn.clicked.connect(self._open_media)
        
        buttons_layout.addWidget(self.play_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.time_label)
        buttons_layout.addStretch()
        buttons_layout.addLayout(volume_layout)
        buttons_layout.addWidget(self.open_btn)
        
        controls_layout.addWidget(self.progress_bar)
        controls_layout.addLayout(buttons_layout)
        
        layout.addWidget(self.video_widget, 1)
        layout.addWidget(self.controls)
    
    def _setup_media_player(self):
        """Setup media player"""
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Connect signals
        self.media_player.positionChanged.connect(self._update_position)
        self.media_player.durationChanged.connect(self._update_duration)
        self.media_player.playbackStateChanged.connect(self._update_play_state)
        
        # Set initial volume
        self.audio_output.setVolume(self._volume / 100.0)
    
    def loadMedia(self, file_path: str):
        """Load media file"""
        if os.path.exists(file_path):
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
    
    def _open_media(self):
        """Open media file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Media", "",
            "Media Files (*.mp4 *.avi *.mov *.mkv *.mp3 *.wav *.flac *.m4a)"
        )
        if file_path:
            self.loadMedia(file_path)
    
    def _toggle_play_pause(self):
        """Toggle play/pause"""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def _stop(self):
        """Stop playback"""
        self.media_player.stop()
    
    def _seek_position(self, position: int):
        """Seek to position"""
        if self._duration > 0:
            seek_position = (position / 1000.0) * self._duration
            self.media_player.setPosition(int(seek_position))
    
    def _set_volume(self, volume: int):
        """Set volume"""
        self._volume = volume
        self.audio_output.setVolume(volume / 100.0)
        
        # Update volume button icon
        if volume == 0:
            self.volume_btn.setText("🔇")
        elif volume < 50:
            self.volume_btn.setText("🔉")
        else:
            self.volume_btn.setText("🔊")
    
    def _toggle_mute(self):
        """Toggle mute"""
        if self.audio_output.volume() > 0:
            self._last_volume = self._volume
            self.volume_slider.setValue(0)
        else:
            self.volume_slider.setValue(getattr(self, '_last_volume', 50))
    
    def _update_position(self, position: int):
        """Update position"""
        self._position = position
        if self._duration > 0:
            progress = int((position / self._duration) * 1000)
            self.progress_bar.setValue(progress)
        
        self._update_time_display()
        self.position_changed.emit(position)
    
    def _update_duration(self, duration: int):
        """Update duration"""
        self._duration = duration
        self._update_time_display()
        self.duration_changed.emit(duration)
    
    def _update_play_state(self, state):
        """Update play state"""
        is_playing = state == QMediaPlayer.PlaybackState.PlayingState
        self._is_playing = is_playing
        
        if is_playing:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")
        
        self.playing_changed.emit(is_playing)
    
    def _update_time_display(self):
        """Update time display"""
        current_time = self._format_time(self._position)
        total_time = self._format_time(self._duration)
        self.time_label.setText(f"{current_time} / {total_time}")
    
    def _format_time(self, ms: int) -> str:
        """Format time in mm:ss"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        
        style_sheet = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border-top: 1px solid {theme.get_color('border').name()};
            }}
            QPushButton {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('primary').name()};
            }}
            QPushButton:pressed {{
                background-color: {theme.get_color('accent_medium').name()};
            }}
            QSlider::groove:horizontal {{
                background-color: {theme.get_color('border').name()};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background-color: {theme.get_color('primary').name()};
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }}
            QSlider::sub-page:horizontal {{
                background-color: {theme.get_color('primary').name()};
                border-radius: 3px;
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                font-size: 12px;
            }}
        """
        
        self.setStyleSheet(style_sheet)
    
    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentRichContentViewer(QWidget):
    """Fluent Design style rich content viewer (HTML/Markdown)"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._content_type = "html"  # html or markdown
        self._zoom_factor = 1.0
        
        self._setup_ui()
        self._setup_style()
        
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(40)
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(12, 6, 12, 6)
        toolbar_layout.setSpacing(8)
        
        # Content type selector
        self.type_btn = QPushButton("HTML")
        self.type_btn.setCheckable(True)
        self.type_btn.clicked.connect(self._toggle_content_type)
        
        # Zoom controls
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setFixedSize(28, 28)
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedSize(28, 28)
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        
        # Open file button
        self.open_btn = QPushButton("Open File")
        self.open_btn.clicked.connect(self._open_file)
        
        toolbar_layout.addWidget(self.type_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.zoom_out_btn)
        toolbar_layout.addWidget(self.zoom_label)
        toolbar_layout.addWidget(self.zoom_in_btn)
        toolbar_layout.addWidget(self.open_btn)
        
        # Content viewer
        self.content_viewer = QTextEdit()
        self.content_viewer.setReadOnly(True)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.content_viewer, 1)
    
    def setContent(self, content: str, content_type: str = "html"):
        """Set content"""
        self._content_type = content_type
        
        if content_type == "html":
            self.content_viewer.setHtml(content)
            self.type_btn.setText("HTML")
        else:
            # For markdown, we'd need to convert to HTML
            # For now, just display as plain text
            self.content_viewer.setPlainText(content)
            self.type_btn.setText("Markdown")
    
    def _open_file(self):
        """Open content file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Content File", "",
            "Content Files (*.html *.htm *.md *.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine content type from extension
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.html', '.htm']:
                    content_type = "html"
                elif ext in ['.md']:
                    content_type = "markdown"
                else:
                    content_type = "plain"
                
                self.setContent(content, content_type)
                
            except Exception as e:
                self.content_viewer.setPlainText(f"Error loading file: {str(e)}")
    
    def _toggle_content_type(self):
        """Toggle between HTML and plain text view"""
        current_content = self.content_viewer.toPlainText()
        
        if self._content_type == "html":
            self.content_viewer.setPlainText(current_content)
            self.type_btn.setText("Plain")
            self._content_type = "plain"
        else:
            self.content_viewer.setHtml(current_content)
            self.type_btn.setText("HTML")
            self._content_type = "html"
    
    def _zoom_in(self):
        """Zoom in"""
        if self._zoom_factor < 3.0:
            self._zoom_factor = min(self._zoom_factor * 1.2, 3.0)
            self._apply_zoom()
    
    def _zoom_out(self):
        """Zoom out"""
        if self._zoom_factor > 0.5:
            self._zoom_factor = max(self._zoom_factor / 1.2, 0.5)
            self._apply_zoom()
    
    def _apply_zoom(self):
        """Apply zoom factor"""
        font = self.content_viewer.font()
        base_size = 11
        font.setPointSize(int(base_size * self._zoom_factor))
        self.content_viewer.setFont(font)
        
        # Update zoom label
        percentage = int(self._zoom_factor * 100)
        self.zoom_label.setText(f"{percentage}%")
    
    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        
        style_sheet = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border-bottom: 1px solid {theme.get_color('border').name()};
            }}
            QPushButton {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('primary').name()};
            }}
            QPushButton:checked {{
                background-color: {theme.get_color('primary').name()};
                color: white;
            }}
            QTextEdit {{
                background-color: {theme.get_color('surface').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                selection-background-color: {theme.get_color('primary').name()};
                selection-color: white;
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                font-size: 11px;
            }}
        """
        
        self.setStyleSheet(style_sheet)
    
    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()


class FluentThumbnailGallery(QWidget):
    """Fluent Design style thumbnail gallery"""
    
    item_selected = Signal(int)  # Selected index
    item_double_clicked = Signal(int)  # Double-clicked index
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._items = []
        self._selected_index = -1
        self._thumbnail_size = QSize(150, 150)
        self._columns = 4
        
        self._setup_ui()
        self._setup_style()
        
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(40)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 6, 8, 6)
        
        # Size slider
        toolbar_layout.addWidget(QLabel("Size:"))
        
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(100)
        self.size_slider.setMaximum(250)
        self.size_slider.setValue(150)
        self.size_slider.setMaximumWidth(100)
        self.size_slider.valueChanged.connect(self._update_thumbnail_size)
        
        toolbar_layout.addWidget(self.size_slider)
        toolbar_layout.addStretch()
        
        # Add folder button
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.clicked.connect(self._add_folder)
        toolbar_layout.addWidget(self.add_folder_btn)
        
        # Gallery area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_widget)
        self.gallery_layout.setSpacing(8)
        
        self.scroll_area.setWidget(self.gallery_widget)
        
        layout.addWidget(toolbar)
        layout.addWidget(self.scroll_area, 1)
    
    def addImagePath(self, file_path: str):
        """Add image by file path"""
        if os.path.exists(file_path):
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.addItem(file_path, pixmap)
    
    def addItem(self, title: str, pixmap: QPixmap):
        """Add thumbnail item"""
        index = len(self._items)
        
        # Create thumbnail item
        item_widget = self._create_thumbnail_item(title, pixmap, index)
        
        # Calculate grid position
        row = index // self._columns
        col = index % self._columns
        
        self.gallery_layout.addWidget(item_widget, row, col)
        
        # Store item info
        self._items.append({
            'title': title,
            'pixmap': pixmap,
            'widget': item_widget
        })
    
    def _create_thumbnail_item(self, title: str, pixmap: QPixmap, index: int):
        """Create thumbnail item widget"""
        item_widget = QFrame()
        item_widget.setFrameStyle(QFrame.Shape.Box)
        item_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Store index as a custom attribute (instead of trying to assign to non-existent property)
        item_widget._item_index = index
        
        layout = QVBoxLayout(item_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Thumbnail image
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setFixedSize(self._thumbnail_size)
        
        # Scale pixmap to fit thumbnail size
        scaled_pixmap = pixmap.scaled(
            self._thumbnail_size, 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        image_label.setPixmap(scaled_pixmap)
        
        # Title label
        title_label = QLabel(os.path.basename(title))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setMaximumHeight(40)
        
        layout.addWidget(image_label)
        layout.addWidget(title_label)
        
        # Event handling
        item_widget.mousePressEvent = lambda event: self._on_item_clicked(index, event)
        
        return item_widget
    
    def _on_item_clicked(self, index: int, event: QMouseEvent):
        """Handle item click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._select_item(index)
            
            # Check for double click
            if hasattr(self, '_last_click_time'):
                if time.time() - self._last_click_time < 0.5:
                    self.item_double_clicked.emit(index)
            
            self._last_click_time = time.time()
    
    def _select_item(self, index: int):
        """Select item"""
        if self._selected_index != index:
            # Deselect previous item
            if 0 <= self._selected_index < len(self._items):
                prev_widget = self._items[self._selected_index]['widget']
                prev_widget.setStyleSheet("")
            
            # Select new item
            self._selected_index = index
            if 0 <= index < len(self._items):
                item_widget = self._items[index]['widget']
                theme = theme_manager
                item_widget.setStyleSheet(f"""
                    QFrame {{
                        border: 2px solid {theme.get_color('primary').name()};
                        background-color: {theme.get_color('accent_light').name()};
                    }}
                """)
            
            self.item_selected.emit(index)
    
    def _update_thumbnail_size(self, size: int):
        """Update thumbnail size"""
        self._thumbnail_size = QSize(size, size)
        
        # Update all existing thumbnails
        for item in self._items:
            widget = item['widget']
            image_label = widget.findChild(QLabel)
            if image_label and hasattr(image_label, 'setFixedSize'):
                image_label.setFixedSize(self._thumbnail_size)
                
                # Rescale pixmap
                scaled_pixmap = item['pixmap'].scaled(
                    self._thumbnail_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                image_label.setPixmap(scaled_pixmap)
    
    def _add_folder(self):
        """Add images from folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            # Supported image extensions
            image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.ico']
            
            for filename in os.listdir(folder):
                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    file_path = os.path.join(folder, filename)
                    self.addImagePath(file_path)
    
    def clearItems(self):
        """Clear all items"""
        for item in self._items:
            item['widget'].deleteLater()
        
        self._items.clear()
        self._selected_index = -1
    
    def _setup_style(self):
        """Setup style"""
        theme = theme_manager
        
        style_sheet = f"""
            QFrame {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
            }}
            QFrame:hover {{
                border-color: {theme.get_color('primary').name()};
                background-color: {theme.get_color('accent_light').name()};
            }}
            QLabel {{
                color: {theme.get_color('text_primary').name()};
                background-color: transparent;
                border: none;
                font-size: 11px;
            }}
            QPushButton {{
                background-color: {theme.get_color('background').name()};
                color: {theme.get_color('text_primary').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme.get_color('accent_light').name()};
                border-color: {theme.get_color('primary').name()};
            }}
            QScrollArea {{
                background-color: {theme.get_color('background').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: 4px;
            }}
        """
        
        self.setStyleSheet(style_sheet)
    
    def _on_theme_changed(self, _):
        """Handle theme change"""
        self._setup_style()
