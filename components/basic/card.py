"""
Fluent Design Style Card Component
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, Property, QByteArray, QTimer
from PySide6.QtGui import QPainter, QPainterPath, QColor, QBrush, QPixmap
from core.theme import theme_manager
from core.animation import FluentAnimation
from core.enhanced_animations import (FluentTransition, FluentMicroInteraction,
                                      FluentRevealEffect, FluentSequence)
from typing import Optional


class FluentCard(QFrame):
    """Fluent Design style card component with enhanced animations"""

    # Signals
    clicked = Signal()
    hoverProgressChanged = Signal(float)
    pressProgressChanged = Signal(float)
    currentElevationChanged = Signal(float)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._clickable = False
        self._elevation = 2
        self._hover_elevation = 4
        self._corner_radius = 8
        self._current_elevation = 2.0
        self._hover_progress = 0.0
        self._press_progress = 0.0

        self._setup_ui()
        self._setup_style()
        self._setup_enhanced_animations()
        self._setup_shadow()

        if theme_manager:
            theme_manager.theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        """Setup UI components"""
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # Main layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)

    def _setup_style(self):
        """Setup component style"""
        theme = theme_manager

        style_sheet = f"""
            FluentCard {{
                background-color: {theme.get_color('surface').name()};
                border: 1px solid {theme.get_color('border').name()};
                border-radius: {self._corner_radius}px;
                transition: all 0.3s ease;
            }}
            FluentCard:hover {{
                border-color: {theme.get_color('primary').name()};
            }}
        """

        self.setStyleSheet(style_sheet)

    def _setup_enhanced_animations(self):
        """Setup enhanced animation system"""
        # Enhanced hover animation
        self._hover_animation = QPropertyAnimation(
            self, QByteArray(b"hover_progress"))
        self._hover_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._hover_animation.setEasingCurve(FluentTransition.EASE_SMOOTH)

        # Enhanced press animation
        self._press_animation = QPropertyAnimation(
            self, QByteArray(b"press_progress"))
        self._press_animation.setDuration(FluentAnimation.DURATION_ULTRA_FAST)
        self._press_animation.setEasingCurve(FluentTransition.EASE_CRISP)

        # Enhanced elevation animation
        self._elevation_animation = QPropertyAnimation(
            self, QByteArray(b"current_elevation"))
        self._elevation_animation.setDuration(FluentAnimation.DURATION_FAST)
        self._elevation_animation.setEasingCurve(FluentTransition.EASE_SPRING)

        # Entrance animation
        QTimer.singleShot(50, self._show_entrance_animation)

    def _show_entrance_animation(self):
        """Show entrance animation with enhanced effects"""
        entrance_sequence = FluentSequence(self)

        # Fade in effect
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.fade_in(self, 300))
        entrance_sequence.addPause(100)

        # Scale in effect with slight bounce
        entrance_sequence.addCallback(
            lambda: FluentRevealEffect.scale_in(self, 250))

        entrance_sequence.start()

    def _setup_shadow(self):
        """Setup drop shadow effect with enhanced styling"""
        self._shadow = QGraphicsDropShadowEffect()
        self._update_shadow()
        self.setGraphicsEffect(self._shadow)

    def _update_shadow(self):
        """Update shadow based on current elevation with enhanced parameters"""
        theme = theme_manager

        blur_radius = self._current_elevation * 3  # Enhanced blur
        offset = max(1, self._current_elevation // 2)  # More subtle offset

        self._shadow.setBlurRadius(blur_radius)
        self._shadow.setOffset(0, offset)

        # Enhanced shadow color with opacity based on elevation
        shadow_color = theme.get_color('shadow')
        shadow_color.setAlpha(
            int(60 + self._current_elevation * 10))  # Dynamic opacity
        self._shadow.setColor(shadow_color)

    # Enhanced property getters and setters
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

    hover_progress = Property(float, _get_hover_progress, _set_hover_progress, None, "",
                              notify=hoverProgressChanged)
    press_progress = Property(float, _get_press_progress, _set_press_progress, None, "",
                              notify=pressProgressChanged)
    current_elevation = Property(float, _get_current_elevation, _set_current_elevation, None, "",
                                 notify=currentElevationChanged)

    def setClickable(self, clickable: bool):
        """Set whether the card is clickable with transition"""
        if self._clickable != clickable:
            self._clickable = clickable

            if clickable:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                # Add hover indication
                FluentMicroInteraction.pulse_animation(self, 1.02)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def isClickable(self) -> bool:
        """Check if the card is clickable"""
        return self._clickable

    def setElevation(self, elevation: int):
        """Set the card elevation with animation"""
        new_elevation = max(0, float(elevation))
        if self._elevation != new_elevation:
            old_elevation = self._current_elevation
            self._elevation = new_elevation

            # Animate elevation change
            self._elevation_animation.setStartValue(old_elevation)
            self._elevation_animation.setEndValue(new_elevation)
            self._elevation_animation.start()

    def getElevation(self) -> int:
        """Get the card elevation"""
        return int(self._elevation)

    def setHoverElevation(self, elevation: int):
        """Set the elevation when hovered with validation"""
        self._hover_elevation = max(self._elevation, float(elevation))

    def getHoverElevation(self) -> int:
        """Get the hover elevation"""
        return int(self._hover_elevation)

    def setCornerRadius(self, radius: int):
        """Set the corner radius with transition"""
        new_radius = max(0, radius)
        if self._corner_radius != new_radius:
            self._corner_radius = new_radius
            self._setup_style()
            FluentMicroInteraction.pulse_animation(self, 1.01)

    def getCornerRadius(self) -> int:
        """Get the corner radius"""
        return self._corner_radius

    # Enhanced layout management methods
    def addWidget(self, widget: QWidget):
        """Add a widget to the card's main layout with animation"""
        widget.setParent(self)
        self._layout.addWidget(widget)

        # Add entrance animation for new widget
        FluentRevealEffect.slide_in(widget, 250, "up")

    def insertWidget(self, index: int, widget: QWidget):
        """Insert a widget at the specified index with animation"""
        widget.setParent(self)
        self._layout.insertWidget(index, widget)

        # Add entrance animation
        FluentRevealEffect.scale_in(widget, 200)

    def removeWidget(self, widget: QWidget):
        """Remove a widget from the card with animation"""
        if widget in [self._layout.itemAt(i).widget() for i in range(self._layout.count())]:
            # Animate removal
            removal_sequence = FluentSequence(self)
            removal_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(widget, 0.0))
            removal_sequence.addPause(200)
            removal_sequence.addCallback(
                lambda: self._complete_widget_removal(widget))
            removal_sequence.start()

    def _complete_widget_removal(self, widget: QWidget):
        """Complete widget removal"""
        self._layout.removeWidget(widget)
        widget.setParent(None)

    def addLayout(self, layout):
        """Add a layout to the card's main layout"""
        self._layout.addLayout(layout)

    def addStretch(self, stretch: int = 0):
        """Add stretch to the card's main layout"""
        self._layout.addStretch(stretch)

    def setMargins(self, left: int, top: int, right: int, bottom: int):
        """Set content margins for the card's main layout with transition"""
        self._layout.setContentsMargins(left, top, right, bottom)
        FluentMicroInteraction.pulse_animation(self, 1.01)

    def setSpacing(self, spacing: int):
        """Set layout spacing for the card's main layout with transition"""
        self._layout.setSpacing(max(0, spacing))
        FluentMicroInteraction.pulse_animation(self, 1.01)

    # Enhanced event handlers
    def enterEvent(self, event):
        """Handle mouse enter with enhanced animation"""
        if self._clickable:
            # Enhanced hover animation
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(1.0)
            self._hover_animation.start()

            # Enhanced elevation animation
            self._elevation_animation.setStartValue(self._current_elevation)
            self._elevation_animation.setEndValue(self._hover_elevation)
            self._elevation_animation.start()

            # Subtle hover glow effect
            FluentMicroInteraction.hover_glow(self, 0.1)

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave with enhanced animation"""
        if self._clickable:
            # Return to normal state
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(0.0)
            self._hover_animation.start()

            # Return elevation to normal
            self._elevation_animation.setStartValue(self._current_elevation)
            self._elevation_animation.setEndValue(self._elevation)
            self._elevation_animation.start()

            # Remove glow effect
            FluentMicroInteraction.hover_glow(self, -0.1)

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press with enhanced animation"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            # Enhanced press animation
            self._press_animation.setStartValue(self._press_progress)
            self._press_animation.setEndValue(1.0)
            self._press_animation.start()

            # Scale down effect
            FluentMicroInteraction.button_press(self, 0.98)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release with enhanced animation"""
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            # Release animation
            self._press_animation.setStartValue(self._press_progress)
            self._press_animation.setEndValue(0.0)
            self._press_animation.start()

            # Emit clicked signal if mouse is still over widget
            if self.rect().contains(event.position().toPoint()):
                # Add ripple effect before emitting signal
                FluentMicroInteraction.ripple_effect(self)
                QTimer.singleShot(100, self.clicked.emit)

        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """Paint the card with enhanced custom effects"""
        super().paintEvent(event)

        if self._hover_progress > 0 or self._press_progress > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Create enhanced card path
            path = QPainterPath()
            rect_adjusted = self.rect().adjusted(1, 1, -1, -1)
            path.addRoundedRect(
                rect_adjusted, self._corner_radius - 1, self._corner_radius - 1)

            # Draw enhanced hover effect
            if self._hover_progress > 0:
                theme = theme_manager
                hover_color = QColor(theme.get_color('accent_light'))
                hover_color.setAlphaF(
                    0.12 * self._hover_progress)  # Enhanced opacity
                painter.fillPath(path, QBrush(hover_color))

            # Draw enhanced press effect
            if self._press_progress > 0:
                theme = theme_manager
                press_color = QColor(theme.get_color('primary'))
                # Subtle press effect
                press_color.setAlphaF(0.08 * self._press_progress)
                painter.fillPath(path, QBrush(press_color))

    def _on_theme_changed(self, _=None):
        """Handle theme change with transition"""
        self._setup_style()
        self._update_shadow()
        FluentMicroInteraction.pulse_animation(self, 1.02)
        self.update()


class FluentImageCard(FluentCard):
    """Card with image header and enhanced image handling"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._image_label: QLabel  # Remove Optional, guaranteed to be created
        self._image_height = 200
        self._original_pixmap: Optional[QPixmap] = None

        self._setup_image_ui()

    def _setup_image_ui(self):
        """Setup image UI with enhanced styling"""
        # Create image label with enhanced properties
        self._image_label = QLabel()  # Now guaranteed to not be None
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setMinimumHeight(self._image_height)
        self._image_label.setMaximumHeight(self._image_height)
        self._image_label.setScaledContents(True)  # Enable scaling

        # Enhanced styling for image area
        theme = theme_manager
        self._image_label.setStyleSheet(f"""
            QLabel {{
                background-color: {theme.get_color('surface_variant').name()};
                border-top-left-radius: {self.getCornerRadius()}px;
                border-top-right-radius: {self.getCornerRadius()}px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
            }}
        """)

        # Insert at the beginning of the main layout
        self._layout.insertWidget(0, self._image_label)

        # Adjust layout margins for image card
        self._layout.setContentsMargins(16, 0, 16, 16)

        # Add entrance animation for image area - now safe without None check
        QTimer.singleShot(100, lambda: FluentRevealEffect.slide_in(
            self._image_label, 300, "up"))

    def setImage(self, pixmap: QPixmap):
        """Set the card image with transition and proper scaling"""
        if not pixmap.isNull():
            self._original_pixmap = pixmap

            # Enhanced scaling with proper aspect ratio handling
            scaled_pixmap = pixmap.scaled(
                self._image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )

            # Create transition effect - now safe without None check
            transition_sequence = FluentSequence(self)
            transition_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self._image_label, 0.95))
            transition_sequence.addPause(150)
            transition_sequence.addCallback(
                lambda: self._image_label.setPixmap(scaled_pixmap))
            transition_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self._image_label, 1.0))
            transition_sequence.start()

    def setImageHeight(self, height: int):
        """Set the image height with animation"""
        new_height = max(100, height)  # Minimum height validation
        if self._image_height != new_height:
            self._image_height = new_height

            # Animate height change - now safe without None check
            old_height = self._image_label.height()

            height_animation = QPropertyAnimation(
                self._image_label, QByteArray(b"minimumHeight"))
            height_animation.setDuration(FluentAnimation.DURATION_MEDIUM)
            height_animation.setEasingCurve(FluentTransition.EASE_SPRING)
            height_animation.setStartValue(old_height)
            height_animation.setEndValue(new_height)
            height_animation.finished.connect(
                lambda: self._image_label.setMaximumHeight(new_height))
            height_animation.start()

            # Re-scale image if it exists
            if self._original_pixmap and not self._original_pixmap.isNull():
                QTimer.singleShot(200, lambda: self.setImage(
                    self._original_pixmap) if self._original_pixmap else None)

    def getImageHeight(self) -> int:
        """Get the current image height"""
        return self._image_height

    def clearImage(self):
        """Clear the image with animation"""
        # Animate image removal - now safe without None check
        clear_sequence = FluentSequence(self)
        clear_sequence.addCallback(lambda: FluentRevealEffect.fade_in(
            self._image_label, 200))  # Fade out
        clear_sequence.addPause(200)
        clear_sequence.addCallback(lambda: self._image_label.clear())
        clear_sequence.addCallback(lambda: FluentRevealEffect.fade_in(
            self._image_label, 200))  # Fade back in
        clear_sequence.start()

        self._original_pixmap = None


class FluentActionCard(FluentCard):
    """Card with action buttons and enhanced action management"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._action_layout: QHBoxLayout  # Remove Optional, guaranteed to be created
        self._action_widgets: list = []

        self._setup_action_ui()

    def _setup_action_ui(self):
        """Setup action UI with enhanced styling"""
        # Create action area at the bottom
        self._action_layout = QHBoxLayout()  # Now guaranteed to not be None
        self._action_layout.setContentsMargins(0, 12, 0, 0)
        self._action_layout.setSpacing(8)  # Enhanced spacing
        self._action_layout.addStretch()  # Right-align actions by default

        # Add separator line above actions
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        theme = theme_manager
        separator.setStyleSheet(f"""
            QFrame {{
                color: {theme.get_color('border').name()};
                background-color: {theme.get_color('border').name()};
                height: 1px;
                border: none;
            }}
        """)

        self._layout.addWidget(separator)
        self._layout.addLayout(self._action_layout)

    def addActionWidget(self, widget: QWidget):
        """Add an action widget with animation"""
        if widget not in self._action_widgets:
            widget.setParent(self)
            self._action_widgets.append(widget)

            # Insert before the stretch - now safe without None check
            self._action_layout.insertWidget(
                self._action_layout.count() - 1, widget)

            # Add entrance animation
            FluentRevealEffect.slide_in(widget, 200, "up")

    def removeActionWidget(self, widget: QWidget):
        """Remove an action widget with animation"""
        if widget in self._action_widgets:
            # Animate removal
            removal_sequence = FluentSequence(self)
            removal_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(widget, 0.0))
            removal_sequence.addPause(200)
            removal_sequence.addCallback(
                lambda: self._complete_action_removal(widget))
            removal_sequence.start()

    def _complete_action_removal(self, widget: QWidget):
        """Complete action widget removal"""
        if widget in self._action_widgets:
            self._action_widgets.remove(widget)
            self._action_layout.removeWidget(
                widget)  # Now safe without None check
            widget.setParent(None)

    def clearActions(self):
        """Clear all action widgets with staggered animation"""
        if self._action_widgets:
            # Staggered removal animation
            for i, widget in enumerate(self._action_widgets.copy()):
                QTimer.singleShot(
                    i * 100, lambda w=widget: self.removeActionWidget(w))

    def getActionCount(self) -> int:
        """Get the number of action widgets"""
        return len(self._action_widgets)

    def setActionAlignment(self, alignment: Qt.AlignmentFlag):
        """Set the alignment of action widgets"""
        # Remove existing stretch - now safe without None check
        for i in range(self._action_layout.count()):
            item = self._action_layout.itemAt(i)
            if item and item.spacerItem():
                self._action_layout.removeItem(item)
                break

        # Add stretch based on alignment
        if alignment == Qt.AlignmentFlag.AlignLeft:
            self._action_layout.addStretch()
        elif alignment == Qt.AlignmentFlag.AlignCenter:
            self._action_layout.insertStretch(0)
            self._action_layout.addStretch()
        elif alignment == Qt.AlignmentFlag.AlignRight:
            self._action_layout.insertStretch(0)

        # Add transition effect
        FluentMicroInteraction.pulse_animation(self, 1.01)


class FluentInfoCard(FluentCard):
    """Specialized card for displaying information with icon and text"""

    def __init__(self, title: str = "", subtitle: str = "", icon: str = "",
                 parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._title_label: QLabel    # Remove Optional, guaranteed to be created
        self._subtitle_label: QLabel  # Remove Optional, guaranteed to be created
        self._icon_label: QLabel     # Remove Optional, guaranteed to be created

        self._setup_info_ui()
        self.setTitle(title)
        self.setSubtitle(subtitle)
        self.setIcon(icon)

    def _setup_info_ui(self):
        """Setup information card UI"""
        # Create header layout for icon and text
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Icon label
        self._icon_label = QLabel()  # Now guaranteed to not be None
        self._icon_label.setFixedSize(48, 48)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setStyleSheet("""
            QLabel {
                border-radius: 24px;
                background-color: rgba(0, 120, 215, 0.1);
                color: #0078d4;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        # Text layout
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        # Title label
        self._title_label = QLabel()  # Now guaranteed to not be None
        title_font = self._title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self._title_label.setFont(title_font)

        # Subtitle label
        self._subtitle_label = QLabel()  # Now guaranteed to not be None
        subtitle_font = self._subtitle_label.font()
        subtitle_font.setPointSize(10)
        self._subtitle_label.setFont(subtitle_font)

        theme = theme_manager
        self._subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.get_color('text_secondary').name()};
            }}
        """)

        text_layout.addWidget(self._title_label)
        text_layout.addWidget(self._subtitle_label)
        text_layout.addStretch()

        header_layout.addWidget(self._icon_label)
        header_layout.addLayout(text_layout)

        # Insert header at the top
        self._layout.insertLayout(0, header_layout)

        # Add entrance animations - now safe without None checks
        QTimer.singleShot(100, lambda: FluentRevealEffect.slide_in(
            self._icon_label, 200, "left"))
        QTimer.singleShot(150, lambda: FluentRevealEffect.slide_in(
            self._title_label, 200, "right"))
        QTimer.singleShot(200, lambda: FluentRevealEffect.slide_in(
            self._subtitle_label, 200, "right"))

    def setTitle(self, title: str):
        """Set the card title with animation"""
        if self._title_label.text() != title:
            self._title_label.setText(title)
            FluentMicroInteraction.pulse_animation(self._title_label, 1.02)

    def setSubtitle(self, subtitle: str):
        """Set the card subtitle with animation"""
        if self._subtitle_label.text() != subtitle:
            self._subtitle_label.setText(subtitle)
            FluentMicroInteraction.pulse_animation(self._subtitle_label, 1.02)

    def setIcon(self, icon: str):
        """Set the card icon with animation"""
        if self._icon_label.text() != icon:
            # Animate icon change - now safe without None checks
            icon_sequence = FluentSequence(self)
            icon_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self._icon_label, 0.8))
            icon_sequence.addPause(100)
            icon_sequence.addCallback(lambda: self._icon_label.setText(icon))
            icon_sequence.addCallback(
                lambda: FluentMicroInteraction.scale_animation(self._icon_label, 1.0))
            icon_sequence.start()

    def getTitle(self) -> str:
        """Get the card title"""
        return self._title_label.text()

    def getSubtitle(self) -> str:
        """Get the card subtitle"""
        return self._subtitle_label.text()

    def getIcon(self) -> str:
        """Get the card icon"""
        return self._icon_label.text()
