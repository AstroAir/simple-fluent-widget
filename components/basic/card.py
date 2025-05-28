"""
Fluent Design Style Card Component
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, Property, QByteArray
from PySide6.QtGui import QPainter, QPainterPath, QColor, QBrush, QPixmap
from core.theme import theme_manager
from core.animation import FluentAnimation
from typing import Optional


class FluentCard(QFrame):
    """Fluent Design style card component"""

    # Signals
    clicked = Signal()
    # Signals for property changes (if needed for Property notify)
    hoverProgressChanged = Signal(float)
    pressProgressChanged = Signal(float)
    currentElevationChanged = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._clickable = False
        self._elevation = 2
        self._hover_elevation = 4
        self._corner_radius = 8
        self._current_elevation = 2.0  # Match property type
        self._hover_progress = 0.0
        self._press_progress = 0.0

        self._setup_ui()
        self._setup_style()
        self._setup_animations()
        self._setup_shadow()

        if theme_manager:  # Ensure theme_manager is not None before connecting
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # Main layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)

    def _setup_style(self):
        """Setup style"""
        theme = theme_manager

        style_sheet = f"""
            FluentCard {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: {self._corner_radius}px;
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_animations(self):
        """Setup animations"""
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"))
        # Assuming DURATION_NORMAL is not defined, use DURATION_FAST
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        self._press_animation = QPropertyAnimation(
            self, QByteArray(b"press_progress"))
        self._press_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._press_animation.setEasingCurve(FluentAnimation.EASE_OUT)

        self._elevation_animation = QPropertyAnimation(
            self, QByteArray(b"current_elevation"))
        # Assuming DURATION_NORMAL is not defined, use DURATION_FAST
        self._elevation_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._elevation_animation.setEasingCurve(FluentAnimation.EASE_OUT)

    def _setup_shadow(self):
        """Setup drop shadow effect"""
        self._shadow = QGraphicsDropShadowEffect()
        self._update_shadow()
        self.setGraphicsEffect(self._shadow)

    def _update_shadow(self):
        """Update shadow based on current elevation"""
        theme = theme_manager

        blur_radius = self._current_elevation * 2
        offset = self._current_elevation

        self._shadow.setBlurRadius(blur_radius)
        self._shadow.setOffset(0, offset)
        self._shadow.setColor(theme.get_color('shadow'))

    def _get_hover_progress(self):
        return self._hover_progress

    def _set_hover_progress(self, value):
        if self._hover_progress != value:
            self._hover_progress = value
            self.hoverProgressChanged.emit(value)
            self.update()

    def _get_press_progress(self):
        return self._press_progress

    def _set_press_progress(self, value):
        if self._press_progress != value:
            self._press_progress = value
            self.pressProgressChanged.emit(value)
            self.update()

    def _get_current_elevation(self):
        return self._current_elevation

    def _set_current_elevation(self, value):
        if self._current_elevation != value:
            self._current_elevation = value
            self.currentElevationChanged.emit(value)
            self._update_shadow()

    hover_progress = Property(float, _get_hover_progress,
                              _set_hover_progress, None, "", notify=hoverProgressChanged)
    press_progress = Property(float, _get_press_progress,
                              _set_press_progress, None, "", notify=pressProgressChanged)
    current_elevation = Property(float, _get_current_elevation,
                                 _set_current_elevation, None, "", notify=currentElevationChanged)

    def setClickable(self, clickable: bool):
        """Set whether the card is clickable"""
        self._clickable = clickable
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def isClickable(self) -> bool:
        """Check if the card is clickable"""
        return self._clickable

    def setElevation(self, elevation: int):
        """Set the card elevation (shadow depth)"""
        self._elevation = float(
            elevation)  # Ensure float for consistency with property
        self._current_elevation = float(elevation)
        self._update_shadow()

    def getElevation(self) -> int:
        """Get the card elevation"""
        return int(self._elevation)

    def setHoverElevation(self, elevation: int):
        """Set the elevation when hovered"""
        self._hover_elevation = float(elevation)

    def getHoverElevation(self) -> int:
        """Get the hover elevation"""
        return int(self._hover_elevation)

    def setCornerRadius(self, radius: int):
        """Set the corner radius"""
        self._corner_radius = radius
        self._setup_style()  # Re-apply style to update border-radius
        self.update()  # Ensure repaint for visual consistency

    def getCornerRadius(self) -> int:
        """Get the corner radius"""
        return self._corner_radius

    def addWidget(self, widget: QWidget):
        """Add a widget to the card's main layout"""
        self._layout.addWidget(widget)

    def insertWidget(self, index: int, widget: QWidget):
        """Insert a widget at the specified index in the card's main layout"""
        self._layout.insertWidget(index, widget)

    def removeWidget(self, widget: QWidget):
        """Remove a widget from the card's main layout"""
        self._layout.removeWidget(widget)

    def addLayout(self, layout: QHBoxLayout | QVBoxLayout):  # More specific type hint
        """Add a layout to the card's main layout"""
        self._layout.addLayout(layout)

    def addStretch(self, stretch: int = 0):
        """Add stretch to the card's main layout"""
        self._layout.addStretch(stretch)

    def setMargins(self, left: int, top: int, right: int, bottom: int):
        """Set content margins for the card's main layout"""
        self._layout.setContentsMargins(left, top, right, bottom)

    def setSpacing(self, spacing: int):
        """Set layout spacing for the card's main layout"""
        self._layout.setSpacing(spacing)

    def enterEvent(self, event):
        """Handle mouse enter"""
        if self._clickable:
            # Start hover animations
            self._hover_animation.setStartValue(
                self._hover_progress)  # Use private attribute
            self._hover_animation.setEndValue(1.0)
            self._hover_animation.start()

            self._elevation_animation.setStartValue(
                self._current_elevation)  # Use private attribute
            self._elevation_animation.setEndValue(self._hover_elevation)
            self._elevation_animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        if self._clickable:
            # End hover animations
            self._hover_animation.setStartValue(
                self._hover_progress)  # Use private attribute
            self._hover_animation.setEndValue(0.0)
            self._hover_animation.start()

            self._elevation_animation.setStartValue(
                self._current_elevation)  # Use private attribute
            self._elevation_animation.setEndValue(self._elevation)
            self._elevation_animation.start()

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            # Start press animation
            self._press_animation.setStartValue(
                self._press_progress)  # Use private attribute
            self._press_animation.setEndValue(1.0)
            self._press_animation.start()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            # End press animation
            self._press_animation.setStartValue(
                self._press_progress)  # Use private attribute
            self._press_animation.setEndValue(0.0)
            self._press_animation.start()

            # Emit clicked signal if mouse is still over widget
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()

        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """Paint the card with custom effects"""
        super().paintEvent(event)  # Call QFrame's paintEvent first

        # Custom painting for hover/press effects should happen after super().paintEvent()
        # if they are overlays. If they are part of the background, QFrame's style sheet handles it.
        # The current implementation draws overlays.

        if self._hover_progress > 0 or self._press_progress > 0:  # Use private attributes
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Create card path
            path = QPainterPath()
            # Adjust rect slightly if border is 1px to draw inside the border
            rect_adjusted = self.rect().adjusted(1, 1, -1, -1)
            # Adjust radius if drawing inside
            path.addRoundedRect(
                rect_adjusted, self._corner_radius - 1, self._corner_radius - 1)

            # Draw hover effect
            if self._hover_progress > 0:
                theme = theme_manager
                # Ensure QColor for setAlphaF
                hover_color = QColor(theme.get_color('accent_light'))
                hover_color.setAlphaF(0.1 * self._hover_progress)
                painter.fillPath(path, QBrush(hover_color))

            # Draw press effect
            if self._press_progress > 0:
                theme = theme_manager
                # Ensure QColor for setAlphaF
                press_color = QColor(theme.get_color('primary'))
                press_color.setAlphaF(0.05 * self._press_progress)
                painter.fillPath(path, QBrush(press_color))

    def _on_theme_changed(self, _=None):  # Add default for argument
        """Handle theme change"""
        self._setup_style()
        self._update_shadow()
        self.update()  # Trigger repaint


class FluentImageCard(FluentCard):
    """Card with image header"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._image_label: Optional[QLabel] = None  # Initialize with type hint
        self._image_height = 200

        self._setup_image_ui()

    def _setup_image_ui(self):
        """Setup image UI"""
        # Insert image label at the top
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setMinimumHeight(self._image_height)
        # Ensure image label respects corner radius if it's the topmost element
        # The stylesheet here might conflict with FluentCard's overall border-radius
        # It's often better to clip the pixmap or use a mask on the QLabel.
        self._image_label.setStyleSheet(f"""
            QLabel {{
                background-color: #f0f0f0; /* Placeholder, ideally from theme */
                border-top-left-radius: {self.getCornerRadius()}px;
                border-top-right-radius: {self.getCornerRadius()}px;
                border-bottom-left-radius: 0px; /* If content follows */
                border-bottom-right-radius: 0px; /* If content follows */
            }}
        """)

        # Insert at the beginning of the main layout
        self._layout.insertWidget(0, self._image_label)

        # Adjust margins: top margin is now handled by the image label or its content
        # The card's main layout content margins might need to be (16, 0, 16, 16)
        # if the image is truly edge-to-edge at the top.
        # The original (16,0,16,16) was for _layout, which is correct.
        # No, the original card margins are (16,16,16,16). If image is at top,
        # the layout's top margin should be 0, and image label handles its own padding if needed.
        self._layout.setContentsMargins(self._layout.contentsMargins().left(
        ), 0, self._layout.contentsMargins().right(), self._layout.contentsMargins().bottom())

    def setImage(self, pixmap: QPixmap):
        """Set the card image"""
        if self._image_label:
            # Scale pixmap to fill the label width, maintaining aspect ratio, then crop height
            # or scale to fit height, maintaining aspect ratio, then crop width.
            # KeepAspectRatioByExpanding will ensure it covers, then it will be clipped by QLabel.
            scaled_pixmap = pixmap.scaled(
                self._image_label.width(),  # Scale to label's width
                self._image_height,        # Target height for scaling
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,  # Cover the area
                Qt.TransformationMode.SmoothTransformation
            )
            # Center crop if necessary, QLabel usually handles this by alignment or size policy
            self._image_label.setPixmap(scaled_pixmap)

    def setImageHeight(self, height: int):
        """Set the image height"""
        self._image_height = height
        if self._image_label:
            self._image_label.setMinimumHeight(height)
            self._image_label.setMaximumHeight(height)  # Fix height
            # If image is already set, rescale it
            if self._image_label.pixmap() and not self._image_label.pixmap().isNull():
                # Re-call setImage to re-scale
                self.setImage(self._image_label.pixmap())


class FluentActionCard(FluentCard):
    """Card with action buttons"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Initialize with type hint
        self._action_layout: Optional[QHBoxLayout] = None
        self._setup_action_ui()

    def _setup_action_ui(self):
        """Setup action UI"""
        # Add action area at the bottom of the main layout
        self._action_layout = QHBoxLayout()
        self._action_layout.setContentsMargins(
            0, 12, 0, 0)  # Top margin for spacing
        self._action_layout.addStretch()  # For right-aligning actions by default

        self._layout.addLayout(self._action_layout)

    def add_action_widget(self, widget: QWidget):  # Renamed from addAction
        """Add an action widget (like a button) to the action area"""
        if self._action_layout:
            # Insert before the stretch to keep actions on the left of stretch
            self._action_layout.insertWidget(
                self._action_layout.count() - 1, widget)

    def remove_action_widget(self, widget: QWidget):  # Renamed from removeAction
        """Remove an action widget from the action area"""
        if self._action_layout:
            self._action_layout.removeWidget(widget)
            widget.setParent(None)  # Explicitly reparent
