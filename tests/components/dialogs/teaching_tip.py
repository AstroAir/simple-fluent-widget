import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
from PySide6.QtGui import QFont, QIcon, QColor, QPixmap
from components.dialogs.teaching_tip import FluentTeachingTip, TeachingTipPlacement, TeachingTipIcon

# filepath: components/dialogs/test_teaching_tip.py

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QGraphicsDropShadowEffect,
                               QSizePolicy)
from PySide6.QtCore import (Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve,
                            QSize, QRect, QPoint, QByteArray)

# Add the project root to the path if necessary for relative imports
# Assuming the test file is in components/dialogs/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Mock base classes to avoid external dependencies during unit tests
# from components.base.fluent_control_base import FluentControlBase, FluentThemeAware


class TestFluentTeachingTip(unittest.TestCase):
    """Test suite for FluentTeachingTip."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up for each test."""
        # Patch base class initializations
        with patch('components.base.fluent_control_base.FluentControlBase.__init__', return_value=None) as mock_base_control_init, \
             patch('components.base.fluent_control_base.FluentThemeAware.__init__', return_value=None) as mock_base_theme_init:
            self.dialog = FluentTeachingTip()
            self.mock_base_control_init = mock_base_control_init
            self.mock_base_theme_init = mock_base_theme_init

        self.parent = QWidget()
        self.target_widget = QWidget(self.parent)
        self.target_widget.setGeometry(100, 100, 50, 30) # Set a geometry for testing position

        # Ensure UI elements are created for tests that rely on them
        self.dialog._setup_ui()
        self.dialog._setup_animations() # Ensure animations are setup

    def tearDown(self):
        """Tear down after each test."""
        if self.dialog:
            self.dialog.close()
            self.dialog.deleteLater()
        if self.parent:
            self.parent.close()
            self.parent.deleteLater()
        QApplication.processEvents() # Process events to clean up widgets

    def test_init_defaults(self):
        """Test the initialization with default parameters."""
        # Re-create dialog to test init directly without setup_ui side effects
        with patch('components.base.fluent_control_base.FluentControlBase.__init__', return_value=None) as mock_base_control_init, \
             patch('components.base.fluent_control_base.FluentThemeAware.__init__', return_value=None) as mock_base_theme_init, \
             patch.object(FluentTeachingTip, '_setup_ui') as mock_setup_ui, \
             patch.object(FluentTeachingTip, '_setup_styling') as mock_setup_styling, \
             patch.object(FluentTeachingTip, '_setup_connections') as mock_setup_connections, \
             patch.object(FluentTeachingTip, '_setup_accessibility') as mock_setup_accessibility, \
             patch.object(FluentTeachingTip, '_setup_animations') as mock_setup_animations, \
             patch.object(FluentTeachingTip, 'apply_theme') as mock_apply_theme, \
             patch.object(FluentTeachingTip, 'hide') as mock_hide:

            dialog = FluentTeachingTip(self.parent)

            mock_base_control_init.assert_called_once_with(dialog)
            mock_base_theme_init.assert_called_once_with(dialog)

            self.assertEqual(dialog._title, "")
            self.assertEqual(dialog._subtitle, "")
            self.assertEqual(dialog._icon, TeachingTipIcon.NONE)
            self.assertIsNone(dialog._custom_icon)
            self.assertEqual(dialog._placement, TeachingTipPlacement.AUTO)
            self.assertIsNone(dialog._target_widget)
            self.assertEqual(dialog._actions, [])
            self.assertTrue(dialog._is_light_dismiss_enabled)
            self.assertEqual(dialog._auto_hide_duration, 0)
            self.assertFalse(dialog._is_visible)
            self.assertFalse(dialog._is_animating)

            self.assertIsInstance(dialog._auto_hide_timer, QTimer)
            self.assertTrue(dialog._auto_hide_timer.isSingleShot())
            # Cannot easily check signal connection without more complex mocking

            mock_setup_ui.assert_called_once()
            mock_setup_styling.assert_called_once()
            mock_setup_connections.assert_called_once()
            mock_setup_accessibility.assert_called_once()
            mock_setup_animations.assert_called_once()
            mock_apply_theme.assert_called_once()
            mock_hide.assert_called_once()

            dialog.deleteLater() # Clean up the temporary dialog

    def test_setup_ui(self):
        """Test the _setup_ui method."""
        # _setup_ui is called in setUp, check its effects
        self.assertTrue(self.dialog.windowFlags() & Qt.WindowType.FramelessWindowHint)
        self.assertTrue(self.dialog.windowFlags() & Qt.WindowType.Tool)
        self.assertTrue(self.dialog.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))

        self.assertIsNotNone(self.dialog._container)
        self.assertIsInstance(self.dialog._container, QFrame)
        self.assertIsNotNone(self.dialog._container.graphicsEffect())
        self.assertIsInstance(self.dialog._container.graphicsEffect(), QGraphicsDropShadowEffect)

        self.assertIsNotNone(self.dialog._header_layout)
        self.assertIsNotNone(self.dialog._icon_label)
        self.assertIsNotNone(self.dialog._title_label)
        self.assertIsNotNone(self.dialog._close_button)
        self.assertIsNotNone(self.dialog._subtitle_label)
        self.assertIsNotNone(self.dialog._actions_layout)

        self.assertEqual(self.dialog.sizePolicy().horizontalPolicy(), QSizePolicy.Policy.Preferred)
        self.assertEqual(self.dialog.sizePolicy().verticalPolicy(), QSizePolicy.Policy.Preferred)

    @patch.object(FluentTeachingTip, 'get_current_theme', return_value={'surface_primary': '#fff', 'stroke_default': '#ccc', 'text_primary': '#000', 'text_secondary': '#555', 'accent_default': '#0078d4'})
    def test_setup_styling(self, mock_get_theme):
        """Test the _setup_styling method."""
        self.dialog._setup_styling()
        mock_get_theme.assert_called_once()
        # Basic check that stylesheets are applied (cannot easily check content without parsing)
        self.assertTrue(len(self.dialog._container.styleSheet()) > 0)
        self.assertTrue(len(self.dialog._title_label.styleSheet()) > 0)
        self.assertTrue(len(self.dialog._subtitle_label.styleSheet()) > 0)
        self.assertTrue(len(self.dialog._close_button.styleSheet()) > 0)

    @patch.object(FluentTeachingTip, 'dismiss')
    def test_setup_connections(self, mock_dismiss):
        """Test the _setup_connections method."""
        # _setup_connections is called in setUp, check its effects
        # Simulate clicking the close button
        self.dialog._close_button.clicked.emit()
        mock_dismiss.assert_called_once()

    def test_setup_accessibility(self):
        """Test the _setup_accessibility method."""
        # _setup_accessibility is called in setUp, check its effects
        self.assertEqual(self.dialog.accessibleName(), "Teaching tip")
        self.assertEqual(self.dialog._title_label.accessibleName(), "Teaching tip title")
        self.assertEqual(self.dialog._subtitle_label.accessibleName(), "Teaching tip content")
        self.assertEqual(self.dialog._close_button.accessibleName(), "Close teaching tip")

    def test_setup_animations(self):
        """Test the _setup_animations method."""
        # _setup_animations is called in setUp, check its effects
        self.assertIsNotNone(self.dialog._show_animation)
        self.assertIsInstance(self.dialog._show_animation, QPropertyAnimation)
        self.assertEqual(self.dialog._show_animation.propertyName(), b"windowOpacity")
        self.assertEqual(self.dialog._show_animation.duration(), 250)
        self.assertEqual(self.dialog._show_animation.easingCurve().type(), QEasingCurve.Type.OutCubic)
        self.assertEqual(self.dialog._show_animation.startValue(), 0.0)
        self.assertEqual(self.dialog._show_animation.endValue(), 1.0)
        # Cannot easily check signal connection without more complex mocking

        self.assertIsNotNone(self.dialog._hide_animation)
        self.assertIsInstance(self.dialog._hide_animation, QPropertyAnimation)
        self.assertEqual(self.dialog._hide_animation.propertyName(), b"windowOpacity")
        self.assertEqual(self.dialog._hide_animation.duration(), 150)
        self.assertEqual(self.dialog._hide_animation.easingCurve().type(), QEasingCurve.Type.InCubic)
        self.assertEqual(self.dialog._hide_animation.startValue(), 1.0)
        self.assertEqual(self.dialog._hide_animation.endValue(), 0.0)
        # Cannot easily check signal connection without more complex mocking

    @patch.object(QTimer, 'start')
    def test_on_show_animation_finished(self, mock_timer_start):
        """Test _on_show_animation_finished."""
        shown_spy = MagicMock()
        self.dialog.shown.connect(shown_spy)

        self.dialog._is_animating = True
        self.dialog._auto_hide_duration = 5000
        self.dialog._on_show_animation_finished()

        self.assertFalse(self.dialog._is_animating)
        shown_spy.assert_called_once()
        mock_timer_start.assert_called_once_with(5000)

        # Test without auto-hide
        mock_timer_start.reset_mock()
        self.dialog._is_animating = True
        self.dialog._auto_hide_duration = 0
        self.dialog._on_show_animation_finished()
        mock_timer_start.assert_not_called()

    @patch('PySide6.QtWidgets.QWidget.hide')
    def test_on_hide_animation_finished(self, mock_super_hide):
        """Test _on_hide_animation_finished."""
        hidden_spy = MagicMock()
        self.dialog.hidden.connect(hidden_spy)

        self.dialog._is_animating = True
        self.dialog._is_visible = True
        self.dialog._on_hide_animation_finished()

        self.assertFalse(self.dialog._is_animating)
        self.assertFalse(self.dialog._is_visible)
        mock_super_hide.assert_called_once()
        hidden_spy.assert_called_once()

    @patch('PySide6.QtWidgets.QApplication.primaryScreen')
    @patch.object(QWidget, 'mapToGlobal', return_value=QPoint(100, 100))
    @patch.object(QWidget, 'size', return_value=QSize(50, 30))
    @patch.object(FluentTeachingTip, 'sizeHint', return_value=QSize(200, 100))
    def test_calculate_position_with_target(self, mock_size_hint, mock_target_size, mock_map_to_global, mock_primary_screen):
        """Test _calculate_position with a target widget."""
        # Mock screen geometry
        mock_screen_geometry = QRect(0, 0, 800, 600)
        mock_primary_screen.return_value.geometry.return_value = mock_screen_geometry

        self.dialog.set_target(self.target_widget)
        tip_size = self.dialog.sizeHint() # QSize(200, 100)
        target_rect = QRect(100, 100, 50, 30) # Global position and size

        # Test default AUTO placement (should pick BOTTOM)
        self.dialog.set_placement(TeachingTipPlacement.AUTO)
        pos = self.dialog._calculate_position()
        # Expected BOTTOM position: target_center_x - tip_width/2, target_bottom + margin
        # target_center_x = 100 + 50/2 = 125
        # target_bottom = 100 + 30 = 130
        # Expected x = 125 - 200/2 = 25
        # Expected y = 130 + 8 = 138
        self.assertEqual(pos, QPoint(25, 138))

        # Test explicit BOTTOM placement
        self.dialog.set_placement(TeachingTipPlacement.BOTTOM)
        pos = self.dialog._calculate_position()
        self.assertEqual(pos, QPoint(25, 138))

        # Test explicit TOP placement
        self.dialog.set_placement(TeachingTipPlacement.TOP)
        pos = self.dialog._calculate_position()
        # Expected TOP position: target_center_x - tip_width/2, target_top - tip_height - margin
        # target_center_x = 125
        # target_top = 100
        # Expected x = 125 - 200/2 = 25
        # Expected y = 100 - 100 - 8 = -8
        self.assertEqual(pos, QPoint(25, -8))

        # Test explicit RIGHT placement
        self.dialog.set_placement(TeachingTipPlacement.RIGHT)
        pos = self.dialog._calculate_position()
        # Expected RIGHT position: target_right + margin, target_center_y - tip_height/2
        # target_right = 100 + 50 = 150
        # target_center_y = 100 + 30/2 = 115
        # Expected x = 150 + 8 = 158
        # Expected y = 115 - 100/2 = 65
        self.assertEqual(pos, QPoint(158, 65))

        # Test explicit LEFT placement
        self.dialog.set_placement(TeachingTipPlacement.LEFT)
        pos = self.dialog._calculate_position()
        # Expected LEFT position: target_left - tip_width - margin, target_center_y - tip_height/2
        # target_left = 100
        # target_center_y = 115
        # Expected x = 100 - 200 - 8 = -108
        # Expected y = 115 - 100/2 = 65
        self.assertEqual(pos, QPoint(-108, 65))

        # Test explicit TOP_LEFT placement
        self.dialog.set_placement(TeachingTipPlacement.TOP_LEFT)
        pos = self.dialog._calculate_position()
        # Expected TOP_LEFT position: target_left, target_top - tip_height - margin
        # target_left = 100
        # target_top = 100
        # Expected x = 100
        # Expected y = 100 - 100 - 8 = -8
        self.assertEqual(pos, QPoint(100, -8))

        # Test explicit TOP_RIGHT placement
        self.dialog.set_placement(TeachingTipPlacement.TOP_RIGHT)
        pos = self.dialog._calculate_position()
        # Expected TOP_RIGHT position: target_right - tip_width, target_top - tip_height - margin
        # target_right = 150
        # target_top = 100
        # Expected x = 150 - 200 = -50
        # Expected y = 100 - 100 - 8 = -8
        self.assertEqual(pos, QPoint(-50, -8))

        # Test explicit BOTTOM_LEFT placement
        self.dialog.set_placement(TeachingTipPlacement.BOTTOM_LEFT)
        pos = self.dialog._calculate_position()
        # Expected BOTTOM_LEFT position: target_left, target_bottom + margin
        # target_left = 100
        # target_bottom = 130
        # Expected x = 100
        # Expected y = 130 + 8 = 138
        self.assertEqual(pos, QPoint(100, 138))

        # Test explicit BOTTOM_RIGHT placement
        self.dialog.set_placement(TeachingTipPlacement.BOTTOM_RIGHT)
        pos = self.dialog._calculate_position()
        # Expected BOTTOM_RIGHT position: target_right - tip_width, target_bottom + margin
        # target_right = 150
        # target_bottom = 130
        # Expected x = 150 - 200 = -50
        # Expected y = 130 + 8 = 138
        self.assertEqual(pos, QPoint(-50, 138))


    @patch('PySide6.QtWidgets.QApplication.primaryScreen')
    @patch.object(QWidget, 'mapToGlobal', return_value=QPoint(100, 100))
    @patch.object(QWidget, 'size', return_value=QSize(50, 30))
    @patch.object(FluentTeachingTip, 'sizeHint', return_value=QSize(200, 100))
    def test_determine_best_placement(self, mock_size_hint, mock_target_size, mock_map_to_global, mock_primary_screen):
        """Test _determine_best_placement logic."""
        tip_size = QSize(200, 100)
        target_rect = QRect(100, 100, 50, 30)

        # Case 1: Plenty of space everywhere (should prefer BOTTOM)
        screen_rect = QRect(0, 0, 800, 600)
        mock_primary_screen.return_value.geometry.return_value = screen_rect
        placement = self.dialog._determine_best_placement(target_rect, tip_size, screen_rect)
        self.assertEqual(placement, TeachingTipPlacement.BOTTOM)

        # Case 2: Not enough space below, but space above (should pick TOP)
        screen_rect = QRect(0, 0, 800, 150) # Screen height is small
        mock_primary_screen.return_value.geometry.return_value = screen_rect
        placement = self.dialog._determine_best_placement(target_rect, tip_size, screen_rect)
        self.assertEqual(placement, TeachingTipPlacement.TOP)

        # Case 3: Not enough space below or above, but space right (should pick RIGHT)
        screen_rect = QRect(0, 90, 200, 50) # Screen is narrow and vertically centered around target
        mock_primary_screen.return_value.geometry.return_value = screen_rect
        placement = self.dialog._determine_best_placement(target_rect, tip_size, screen_rect)
        self.assertEqual(placement, TeachingTipPlacement.RIGHT)

        # Case 4: Not enough space below, above, or right, but space left (should pick LEFT)
        screen_rect = QRect(120, 90, 200, 50) # Screen is narrow and vertically centered, target is near left edge
        mock_primary_screen.return_value.geometry.return_value = screen_rect
        placement = self.dialog._determine_best_placement(target_rect, tip_size, screen_rect)
        self.assertEqual(placement, TeachingTipPlacement.LEFT)

        # Case 5: Not enough space anywhere (should fallback to BOTTOM)
        screen_rect = QRect(110, 110, 20, 20) # Screen is smaller than target
        mock_primary_screen.return_value.geometry.return_value = screen_rect
        placement = self.dialog._determine_best_placement(target_rect, tip_size, screen_rect)
        self.assertEqual(placement, TeachingTipPlacement.BOTTOM)


    def test_calculate_position_no_target(self):
        """Test _calculate_position with no target widget (should center)."""
        self.dialog.set_target(None)
        # Mock screen geometry and sizeHint
        with patch('PySide6.QtWidgets.QApplication.primaryScreen') as mock_primary_screen, \
             patch.object(FluentTeachingTip, 'sizeHint', return_value=QSize(300, 200)):
            mock_screen_geometry = QRect(0, 0, 800, 600)
            mock_primary_screen.return_value.geometry.return_value = mock_screen_geometry

            pos = self.dialog._calculate_position()
            # Expected centered position: (screen_width - tip_width)/2, (screen_height - tip_height)/2
            # Expected x = (800 - 300) // 2 = 250
            # Expected y = (600 - 200) // 2 = 200
            self.assertEqual(pos, QPoint(250, 200))

    def test_update_icon_none(self):
        """Test _update_icon with TeachingTipIcon.NONE."""
        self.dialog.set_icon(TeachingTipIcon.NONE)
        self.assertFalse(self.dialog._icon_label.isVisible())
        self.assertEqual(self.dialog._icon_label.text(), "")
        self.assertIsNone(self.dialog._icon_label.pixmap())

    def test_update_icon_predefined(self):
        """Test _update_icon with a pre-defined icon."""
        self.dialog.set_icon(TeachingTipIcon.INFO)
        self.assertTrue(self.dialog._icon_label.isVisible())
        self.assertEqual(self.dialog._icon_label.text(), self.dialog._get_icon_text(TeachingTipIcon.INFO))
        self.assertIsNone(self.dialog._icon_label.pixmap()) # Should use text for predefined

        self.dialog.set_icon(TeachingTipIcon.WARNING)
        self.assertTrue(self.dialog._icon_label.isVisible())
        self.assertEqual(self.dialog._icon_label.text(), self.dialog._get_icon_text(TeachingTipIcon.WARNING))

    def test_update_icon_custom(self):
        """Test _update_icon with a custom QIcon."""
        custom_icon = QIcon(QPixmap(16, 16)) # Create a dummy icon
        self.dialog.set_icon(custom_icon)
        self.assertTrue(self.dialog._icon_label.isVisible())
        self.assertEqual(self.dialog._icon, TeachingTipIcon.NONE) # Internal state should reflect NONE
        self.assertIs(self.dialog._custom_icon, custom_icon)
        self.assertIsNotNone(self.dialog._icon_label.pixmap()) # Should use pixmap for custom

    def test_get_icon_text(self):
        """Test _get_icon_text mapping."""
        self.assertEqual(self.dialog._get_icon_text(TeachingTipIcon.INFO), "ℹ️")
        self.assertEqual(self.dialog._get_icon_text(TeachingTipIcon.WARNING), "⚠️")
        self.assertEqual(self.dialog._get_icon_text(TeachingTipIcon.ERROR), "❌")
        self.assertEqual(self.dialog._get_icon_text(TeachingTipIcon.SUCCESS), "✅")
        self.assertEqual(self.dialog._get_icon_text(TeachingTipIcon.LIGHTBULB), "💡")
        self.assertEqual(self.dialog._get_icon_text(TeachingTipIcon.QUESTION), "❓")
        self.assertEqual(self.dialog._get_icon_text(TeachingTipIcon.NONE), "") # Should return empty for NONE

    @patch.object(FluentTeachingTip, 'get_current_theme', return_value={'accent_default': '#0078d4'})
    def test_update_actions(self, mock_get_theme):
        """Test _update_actions method."""
        # Ensure actions layout is empty initially except for the stretch
        self.assertEqual(self.dialog._actions_layout.count(), 1) # The stretch item

        callback1 = MagicMock()
        callback2 = MagicMock()

        self.dialog.add_action("Action 1", callback1)
        self.dialog.add_action("Action 2", callback2)

        # Check that buttons were added
        self.assertEqual(self.dialog._actions_layout.count(), 3) # Stretch + 2 buttons
        btn1 = self.dialog._actions_layout.itemAt(0).widget()
        btn2 = self.dialog._actions_layout.itemAt(1).widget()
        self.assertIsInstance(btn1, QPushButton)
        self.assertIsInstance(btn2, QPushButton)
        self.assertEqual(btn1.text(), "Action 1")
        self.assertEqual(btn2.text(), "Action 2")

        # Check button connections (cannot directly check callback connection easily)
        # Simulate clicking the first button
        action_clicked_spy = MagicMock()
        self.dialog.action_clicked.connect(action_clicked_spy)
        btn1.clicked.emit()
        action_clicked_spy.assert_called_once_with("Action 1")
        callback1.assert_called_once()
        callback2.assert_not_called()

        # Simulate clicking the second button
        action_clicked_spy.reset_mock()
        callback1.reset_mock()
        btn2.clicked.emit()
        action_clicked_spy.assert_called_once_with("Action 2")
        callback1.assert_not_called()
        callback2.assert_called_once()

        # Test clear_actions
        self.dialog.clear_actions()
        self.assertEqual(self.dialog._actions, [])
        self.assertEqual(self.dialog._actions_layout.count(), 1) # Only the stretch should remain

    def test_set_get_title(self):
        """Test setting and getting the title."""
        self.dialog.set_title("New Title")
        self.assertEqual(self.dialog._title, "New Title")
        self.assertEqual(self.dialog._title_label.text(), "New Title")
        self.assertTrue(self.dialog._title_label.isVisible())
        self.assertEqual(self.dialog.get_title(), "New Title")

        self.dialog.set_title("")
        self.assertEqual(self.dialog._title, "")
        self.assertEqual(self.dialog._title_label.text(), "")
        self.assertFalse(self.dialog._title_label.isVisible())
        self.assertEqual(self.dialog.get_title(), "")

    def test_set_get_subtitle(self):
        """Test setting and getting the subtitle."""
        self.dialog.set_subtitle("New Subtitle")
        self.assertEqual(self.dialog._subtitle, "New Subtitle")
        self.assertEqual(self.dialog._subtitle_label.text(), "New Subtitle")
        self.assertTrue(self.dialog._subtitle_label.isVisible())
        self.assertEqual(self.dialog.get_subtitle(), "New Subtitle")

        self.dialog.set_subtitle("")
        self.assertEqual(self.dialog._subtitle, "")
        self.assertEqual(self.dialog._subtitle_label.text(), "")
        self.assertFalse(self.dialog._subtitle_label.isVisible())
        self.assertEqual(self.dialog.get_subtitle(), "")

    def test_set_get_icon(self):
        """Test setting and getting the icon."""
        # Test predefined icon
        self.dialog.set_icon(TeachingTipIcon.WARNING)
        self.assertEqual(self.dialog._icon, TeachingTipIcon.WARNING)
        self.assertIsNone(self.dialog._custom_icon)
        self.assertEqual(self.dialog.get_icon(), TeachingTipIcon.WARNING)

        # Test custom icon
        custom_icon = QIcon()
        self.dialog.set_icon(custom_icon)
        self.assertEqual(self.dialog._icon, TeachingTipIcon.NONE)
        self.assertIs(self.dialog._custom_icon, custom_icon)
        self.assertIs(self.dialog.get_icon(), custom_icon)

    def test_set_get_placement(self):
        """Test setting and getting the placement."""
        self.dialog.set_placement(TeachingTipPlacement.TOP)
        self.assertEqual(self.dialog._placement, TeachingTipPlacement.TOP)
        self.assertEqual(self.dialog.get_placement(), TeachingTipPlacement.TOP)

        self.dialog.set_placement(TeachingTipPlacement.LEFT)
        self.assertEqual(self.dialog._placement, TeachingTipPlacement.LEFT)
        self.assertEqual(self.dialog.get_placement(), TeachingTipPlacement.LEFT)

    def test_set_get_target(self):
        """Test setting and getting the target widget."""
        self.dialog.set_target(self.target_widget)
        self.assertIs(self.dialog._target_widget, self.target_widget)
        self.assertIs(self.dialog.get_target(), self.target_widget)

        self.dialog.set_target(None)
        self.assertIsNone(self.dialog._target_widget)
        self.assertIsNone(self.dialog.get_target())

    def test_add_action(self):
        """Test adding an action."""
        self.assertEqual(len(self.dialog._actions), 0)
        callback = MagicMock()
        self.dialog.add_action("Test Action", callback)
        self.assertEqual(len(self.dialog._actions), 1)
        self.assertEqual(self.dialog._actions[0], ("Test Action", callback))
        # _update_actions is called internally, tested in test_update_actions

    def test_clear_actions(self):
        """Test clearing actions."""
        self.dialog.add_action("Action 1")
        self.dialog.add_action("Action 2")
        self.assertEqual(len(self.dialog._actions), 2)
        self.dialog.clear_actions()
        self.assertEqual(len(self.dialog._actions), 0)
        # _update_actions is called internally, tested in test_update_actions

    def test_set_get_light_dismiss_enabled(self):
        """Test setting and getting light dismiss enabled state."""
        self.dialog.set_light_dismiss_enabled(False)
        self.assertFalse(self.dialog._is_light_dismiss_enabled)
        self.assertFalse(self.dialog.is_light_dismiss_enabled())

        self.dialog.set_light_dismiss_enabled(True)
        self.assertTrue(self.dialog._is_light_dismiss_enabled)
        self.assertTrue(self.dialog.is_light_dismiss_enabled())

    def test_set_get_auto_hide_duration(self):
        """Test setting and getting auto-hide duration."""
        self.dialog.set_auto_hide_duration(5000)
        self.assertEqual(self.dialog._auto_hide_duration, 5000)
        self.assertEqual(self.dialog.get_auto_hide_duration(), 5000)

        self.dialog.set_auto_hide_duration(-100) # Should clamp to 0
        self.assertEqual(self.dialog._auto_hide_duration, 0)
        self.assertEqual(self.dialog.get_auto_hide_duration(), 0)

    @patch.object(FluentTeachingTip, 'show')
    @patch.object(FluentTeachingTip, 'set_target')
    @patch.object(FluentTeachingTip, 'set_placement')
    def test_show_at(self, mock_set_placement, mock_set_target, mock_show):
        """Test show_at method."""
        self.dialog.show_at(self.target_widget, TeachingTipPlacement.TOP)
        mock_set_target.assert_called_once_with(self.target_widget)
        mock_set_placement.assert_called_once_with(TeachingTipPlacement.TOP)
        mock_show.assert_called_once()

        mock_set_target.reset_mock()
        mock_set_placement.reset_mock()
        mock_show.reset_mock()

        self.dialog.show_at(self.target_widget) # Test without placement
        mock_set_target.assert_called_once_with(self.target_widget)
        mock_set_placement.assert_not_called()
        mock_show.assert_called_once()

    @patch.object(FluentTeachingTip, '_calculate_position', return_value=QPoint(10, 20))
    @patch('PySide6.QtWidgets.QWidget.show')
    @patch.object(QPropertyAnimation, 'start')
    def test_show(self, mock_animation_start, mock_super_show, mock_calculate_position):
        """Test the show method."""
        self.dialog._is_visible = False
        self.dialog._is_animating = False
        self.dialog._show_animation = MagicMock(spec=QPropertyAnimation) # Ensure animation exists

        self.dialog.show()

        mock_calculate_position.assert_called_once()
        self.assertEqual(self.dialog.pos(), QPoint(10, 20))
        self.assertEqual(self.dialog.windowOpacity(), 0.0)
        mock_super_show.assert_called_once()
        self.assertTrue(self.dialog._is_visible)
        self.assertTrue(self.dialog._is_animating)
        self.dialog._show_animation.start.assert_called_once()

        # Test calling show when already visible
        mock_calculate_position.reset_mock()
        mock_super_show.reset_mock()
        mock_animation_start.reset_mock()
        self.dialog._is_visible = True
        self.dialog._is_animating = False
        self.dialog.show()
        mock_calculate_position.assert_not_called()
        mock_super_show.assert_not_called()
        mock_animation_start.assert_not_called()

        # Test calling show when animating
        mock_calculate_position.reset_mock()
        mock_super_show.reset_mock()
        mock_animation_start.reset_mock()
        self.dialog._is_visible = False
        self.dialog._is_animating = True
        self.dialog.show()
        mock_calculate_position.assert_not_called()
        mock_super_show.assert_not_called()
        mock_animation_start.assert_not_called()


    @patch('PySide6.QtWidgets.QWidget.hide') # Mock super().hide()
    @patch.object(QTimer, 'stop')
    @patch.object(QPropertyAnimation, 'start')
    def test_hide(self, mock_animation_start, mock_timer_stop, mock_super_hide):
        """Test the hide method."""
        self.dialog._is_visible = True
        self.dialog._is_animating = False
        self.dialog._hide_animation = MagicMock(spec=QPropertyAnimation) # Ensure animation exists

        self.dialog.hide()

        mock_timer_stop.assert_called_once()
        self.assertTrue(self.dialog._is_animating)
        self.dialog._hide_animation.start.assert_called_once()
        mock_super_hide.assert_not_called() # super().hide() is called after animation finishes

        # Test calling hide when already hidden
        mock_timer_stop.reset_mock()
        mock_animation_start.reset_mock()
        self.dialog._is_visible = False
        self.dialog._is_animating = False
        self.dialog.hide()
        mock_timer_stop.assert_not_called()
        mock_animation_start.assert_not_called()

        # Test calling hide when animating
        mock_timer_stop.reset_mock()
        mock_animation_start.reset_mock()
        self.dialog._is_visible = True
        self.dialog._is_animating = True
        self.dialog.hide()
        mock_timer_stop.assert_not_called()
        mock_animation_start.assert_not_called()

    @patch.object(FluentTeachingTip, 'hide')
    def test_dismiss(self, mock_hide):
        """Test the dismiss method."""
        dismissed_spy = MagicMock()
        self.dialog.dismissed.connect(dismissed_spy)

        self.dialog.dismiss()

        dismissed_spy.assert_called_once()
        mock_hide.assert_called_once()

    def test_is_showing(self):
        """Test the is_showing method."""
        self.dialog._is_visible = False
        self.assertFalse(self.dialog.is_showing())
        self.dialog._is_visible = True
        self.assertTrue(self.dialog.is_showing())

    @patch.object(FluentTeachingTip, '_setup_styling')
    @patch.object(FluentTeachingTip, '_update_actions')
    def test_apply_theme(self, mock_update_actions, mock_setup_styling):
        """Test the apply_theme method."""
        self.dialog.apply_theme()
        mock_setup_styling.assert_called_once()
        mock_update_actions.assert_called_once()

    # Test properties
    def test_title_property(self):
        self.dialog.title = "Prop Title"
        self.assertEqual(self.dialog.get_title(), "Prop Title")
        self.assertEqual(self.dialog._title, "Prop Title")

    def test_subtitle_property(self):
        self.dialog.subtitle = "Prop Subtitle"
        self.assertEqual(self.dialog.get_subtitle(), "Prop Subtitle")
        self.assertEqual(self.dialog._subtitle, "Prop Subtitle")

    def test_placement_property(self):
        self.dialog.placement = TeachingTipPlacement.RIGHT
        self.assertEqual(self.dialog.get_placement(), TeachingTipPlacement.RIGHT)
        self.assertEqual(self.dialog._placement, TeachingTipPlacement.RIGHT)

    def test_target_property(self):
        self.dialog.target = self.target_widget
        self.assertIs(self.dialog.get_target(), self.target_widget)
        self.assertIs(self.dialog._target_widget, self.target_widget)


if __name__ == '__main__':
    unittest.main()