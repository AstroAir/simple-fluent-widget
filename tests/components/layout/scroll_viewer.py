import sys
import os
import pytest
from unittest.mock import Mock, patch, call
from PySide6.QtWidgets import QApplication, QWidget, QScrollArea, QScrollBar, QFrame, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation, Signal, QByteArray, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QResizeEvent, QMouseEvent
from components.layout.scroll_viewer import FluentScrollViewer, FluentScrollBar

# filepath: d:\Project\simple-fluent-widget\tests\components\layout\test_scroll_viewer.py


# Add the project root directory to the path for relative import
# Assuming the test file is in tests/components/layout/
# and the source is in components/layout/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Import the classes to test
# Assuming FluentControlBase is in ..base.fluent_control_base
# from components.base.fluent_control_base import FluentControlBase, FluentThemeAware


@pytest.fixture(scope="session")
def app_fixture():
    """Provides a QApplication instance for the test session."""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()

@pytest.fixture(scope="function")
def scroll_viewer_fixture(app_fixture, request):
    """Provides a FluentScrollViewer instance and a list to track widgets for cleanup."""
    # Create a parent widget for the scroll viewer
    parent_widget = QWidget()
    # FluentScrollViewer is a QWidget subclass
    scroll_viewer = FluentScrollViewer(parent_widget)
    widgets_to_clean = [parent_widget] # Track parent widget for cleanup

    def cleanup():
        """Cleans up widgets after each test."""
        for widget in widgets_to_clean:
             if widget and hasattr(widget, 'setParent'):
                 widget.setParent(None)
                 widget.deleteLater() # Schedule for deletion

        # Process events to allow deletion to occur
        QApplication.processEvents()

    request.addfinalizer(cleanup)

    return scroll_viewer, widgets_to_clean, parent_widget

@pytest.fixture(scope="function")
def scroll_bar_fixture(app_fixture, request):
    """Provides a FluentScrollBar instance and a list to track widgets for cleanup."""
    parent_widget = QWidget()
    scroll_bar = FluentScrollBar(Qt.Orientation.Vertical, parent_widget)
    widgets_to_clean = [parent_widget]

    def cleanup():
        for widget in widgets_to_clean:
             if widget and hasattr(widget, 'setParent'):
                 widget.setParent(None)
                 widget.deleteLater()
        QApplication.processEvents()

    request.addfinalizer(cleanup)

    return scroll_bar, widgets_to_clean, parent_widget


class TestFluentScrollBar:
    """Unit tests for FluentScrollBar."""

    @patch('components.layout.scroll_viewer.QScrollBar.__init__', return_value=None)
    @patch('components.layout.scroll_viewer.QTimer')
    @patch('components.layout.scroll_viewer.QPropertyAnimation')
    def test_init(self, mock_animation_class, mock_timer_class, mock_super_init, scroll_bar_fixture):
        """Test initialization."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture

        # Re-initialize to use mocks
        mock_super_init.reset_mock()
        mock_timer_class.reset_mock()
        mock_animation_class.reset_mock()

        scroll_bar.__init__(Qt.Orientation.Vertical, parent_widget)

        mock_super_init.assert_called_once_with(Qt.Orientation.Vertical, parent_widget)
        assert scroll_bar._is_pressed is False
        assert scroll_bar._is_hovered is False
        assert scroll_bar._theme == {}
        # setFixedSize is called, but hard to mock/check directly

        mock_timer_class.assert_called_once()
        assert isinstance(scroll_bar._hide_timer, Mock)
        scroll_bar._hide_timer.setSingleShot.assert_called_once_with(True)
        scroll_bar._hide_timer.timeout.connect.assert_called_once_with(scroll_bar._on_hide_timeout)

        mock_animation_class.assert_called_once_with(scroll_bar, QByteArray(b"opacity"))
        assert isinstance(scroll_bar._fade_animation, Mock)
        scroll_bar._fade_animation.setDuration.assert_called_once_with(150)
        scroll_bar._fade_animation.setEasingCurve.assert_called_once_with(QEasingCurve.Type.OutCubic)
        assert scroll_bar._opacity == 0.0 # Initial value

    @patch.object(FluentScrollBar, '_get_thumb_rect', return_value=QRect(5, 5, 10, 10))
    @patch('components.layout.scroll_viewer.QPainter')
    def test_paintEvent(self, mock_painter_class, mock_get_thumb_rect, scroll_bar_fixture, mocker):
        """Test paintEvent draws background and thumb."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture
        mock_painter = Mock(spec=QPainter)
        mock_painter_class.return_value = mock_painter
        mock_event = Mock()

        # Mock theme colors
        scroll_bar._theme = {
            'scrollbar_background': '#abcdef',
            'scrollbar_thumb': '#123456',
            'scrollbar_thumb_hover': '#789abc',
            'scrollbar_thumb_pressed': '#def012',
        }
        scroll_bar._opacity = 0.5
        scroll_bar.maximum = Mock(return_value=100) # Simulate scrollable content
        scroll_bar.rect = Mock(return_value=QRect(0, 0, 20, 100)) # Simulate scrollbar size

        # Test default state (not hovered, not pressed)
        scroll_bar._is_hovered = False
        scroll_bar._is_pressed = False
        scroll_bar.paintEvent(mock_event)

        # Check background fill
        mock_painter.fillRect.assert_called_once()
        bg_color = mock_painter.fillRect.call_args[0][1]
        assert isinstance(bg_color, QColor)
        assert bg_color.name() == '#abcdef'
        assert bg_color.alphaF() == 0.5

        # Check thumb draw
        mock_get_thumb_rect.assert_called_once()
        mock_painter.setBrush.assert_called_once()
        thumb_brush = mock_painter.setBrush.call_args[0][0]
        assert isinstance(thumb_brush, QBrush)
        thumb_color = thumb_brush.color()
        assert isinstance(thumb_color, QColor)
        assert thumb_color.name() == '#123456' # Default thumb color
        assert thumb_color.alphaF() == 0.5
        mock_painter.drawRoundedRect.assert_called_once_with(mock_get_thumb_rect.return_value, 2, 2)

        # Test hovered state
        mock_painter.reset_mock()
        mock_get_thumb_rect.reset_mock()
        scroll_bar._is_hovered = True
        scroll_bar._is_pressed = False
        scroll_bar.paintEvent(mock_event)
        thumb_brush = mock_painter.setBrush.call_args[0][0]
        thumb_color = thumb_brush.color()
        assert thumb_color.name() == '#789abc' # Hover thumb color

        # Test pressed state
        mock_painter.reset_mock()
        mock_get_thumb_rect.reset_mock()
        scroll_bar._is_hovered = False
        scroll_bar._is_pressed = True
        scroll_bar.paintEvent(mock_event)
        thumb_brush = mock_painter.setBrush.call_args[0][0]
        thumb_color = thumb_brush.color()
        assert thumb_color.name() == '#def012' # Pressed thumb color

        # Test no thumb when maximum is 0
        mock_painter.reset_mock()
        mock_get_thumb_rect.reset_mock()
        scroll_bar.maximum = Mock(return_value=0)
        scroll_bar.paintEvent(mock_event)
        mock_get_thumb_rect.assert_called_once() # Still called
        mock_painter.setBrush.assert_not_called() # No thumb drawn

    def test__get_thumb_rect_vertical(self, scroll_bar_fixture):
        """Test _get_thumb_rect calculation for vertical scrollbar."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture
        scroll_bar.orientation = Mock(return_value=Qt.Orientation.Vertical)
        scroll_bar.rect = Mock(return_value=QRect(0, 0, 12, 100)) # h=100
        scroll_bar.maximum = Mock(return_value=100)
        scroll_bar.pageStep = Mock(return_value=10) # pageStep=10
        scroll_bar.value = Mock(return_value=0) # value=0

        # Thumb height = max(20, (100 * 10) // (100 + 10)) = max(20, 1000 // 110) = max(20, 9) = 20
        # Thumb y = (100 - 20) * 0 // 100 = 0
        # Rect adjusted(2, 0, -2, 0 + 20 - 100) = QRect(2, 0, 8, -80) -> QRect(2, 0, 8, 20) (adjusted rect is (x, y, width, height))
        thumb_rect = scroll_bar._get_thumb_rect()
        assert thumb_rect == QRect(2, 0, 8, 20) # x=2, y=0, width=12-2-2=8, height=20

        # Test value = maximum
        scroll_bar.value = Mock(return_value=100) # value=100
        # Thumb y = (100 - 20) * 100 // 100 = 80
        # Rect adjusted(2, 80, -2, 80 + 20 - 100) = QRect(2, 80, 8, 0) -> QRect(2, 80, 8, 20)
        thumb_rect = scroll_bar._get_thumb_rect()
        assert thumb_rect == QRect(2, 80, 8, 20)

        # Test maximum = 0
        scroll_bar.maximum = Mock(return_value=0)
        thumb_rect = scroll_bar._get_thumb_rect()
        assert thumb_rect == scroll_bar.rect() # Should return full rect

    def test__get_thumb_rect_horizontal(self, scroll_bar_fixture):
        """Test _get_thumb_rect calculation for horizontal scrollbar."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture
        scroll_bar.orientation = Mock(return_value=Qt.Orientation.Horizontal)
        scroll_bar.rect = Mock(return_value=QRect(0, 0, 100, 12)) # w=100
        scroll_bar.maximum = Mock(return_value=100)
        scroll_bar.pageStep = Mock(return_value=10) # pageStep=10
        scroll_bar.value = Mock(return_value=0) # value=0

        # Thumb width = max(20, (100 * 10) // (100 + 10)) = max(20, 9) = 20
        # Thumb x = (100 - 20) * 0 // 100 = 0
        # Rect adjusted(0, 2, 0 + 20 - 100, -2) = QRect(0, 2, -80, 8) -> QRect(0, 2, 20, 8)
        thumb_rect = scroll_bar._get_thumb_rect()
        assert thumb_rect == QRect(0, 2, 20, 8) # x=0, y=2, width=20, height=12-2-2=8

        # Test value = maximum
        scroll_bar.value = Mock(return_value=100) # value=100
        # Thumb x = (100 - 20) * 100 // 100 = 80
        # Rect adjusted(80, 2, 80 + 20 - 100, -2) = QRect(80, 2, 0, 8) -> QRect(80, 2, 20, 8)
        thumb_rect = scroll_bar._get_thumb_rect()
        assert thumb_rect == QRect(80, 2, 20, 8)

    @patch.object(FluentScrollBar, '_show_scrollbar')
    @patch('components.layout.scroll_viewer.QScrollBar.enterEvent')
    def test_enterEvent(self, mock_super_enter, mock_show_scrollbar, scroll_bar_fixture):
        """Test enterEvent."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture
        mock_event = Mock()
        scroll_bar._is_hovered = False # Initial state

        scroll_bar.enterEvent(mock_event)

        mock_super_enter.assert_called_once_with(mock_event)
        assert scroll_bar._is_hovered is True
        mock_show_scrollbar.assert_called_once()

    @patch.object(FluentScrollBar, '_schedule_hide')
    @patch('components.layout.scroll_viewer.QScrollBar.leaveEvent')
    def test_leaveEvent(self, mock_super_leave, mock_schedule_hide, scroll_bar_fixture):
        """Test leaveEvent."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture
        mock_event = Mock()
        scroll_bar._is_hovered = True # Initial state

        # Test not pressed
        scroll_bar._is_pressed = False
        scroll_bar.leaveEvent(mock_event)
        mock_super_leave.assert_called_once_with(mock_event)
        assert scroll_bar._is_hovered is False
        mock_schedule_hide.assert_called_once()

        # Test pressed
        mock_super_leave.reset_mock()
        mock_schedule_hide.reset_mock()
        scroll_bar._is_hovered = True # Reset state
        scroll_bar._is_pressed = True
        scroll_bar.leaveEvent(mock_event)
        mock_super_leave.assert_called_once_with(mock_event)
        assert scroll_bar._is_hovered is False
        mock_schedule_hide.assert_not_called()

    @patch.object(FluentScrollBar, 'update')
    @patch('components.layout.scroll_viewer.QScrollBar.mousePressEvent')
    def test_mousePressEvent(self, mock_super_press, mock_update, scroll_bar_fixture):
        """Test mousePressEvent."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture
        mock_event = Mock()
        scroll_bar._is_pressed = False # Initial state

        scroll_bar.mousePressEvent(mock_event)

        mock_super_press.assert_called_once_with(mock_event)
        assert scroll_bar._is_pressed is True
        mock_update.assert_called_once()

    @patch.object(FluentScrollBar, '_schedule_hide')
    @patch.object(FluentScrollBar, 'update')
    @patch('components.layout.scroll_viewer.QScrollBar.mouseReleaseEvent')
    def test_mouseReleaseEvent(self, mock_super_release, mock_update, mock_schedule_hide, scroll_bar_fixture):
        """Test mouseReleaseEvent."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture
        mock_event = Mock()
        scroll_bar._is_pressed = True # Initial state

        # Test not hovered
        scroll_bar._is_hovered = False
        scroll_bar.mouseReleaseEvent(mock_event)
        mock_super_release.assert_called_once_with(mock_event)
        assert scroll_bar._is_pressed is False
        mock_update.assert_called_once()
        mock_schedule_hide.assert_called_once()

        # Test hovered
        mock_super_release.reset_mock()
        mock_update.reset_mock()
        mock_schedule_hide.reset_mock()
        scroll_bar._is_pressed = True # Reset state
        scroll_bar._is_hovered = True
        scroll_bar.mouseReleaseEvent(mock_event)
        mock_super_release.assert_called_once_with(mock_event)
        assert scroll_bar._is_pressed is False
        mock_update.assert_called_once()
        mock_schedule_hide.assert_not_called()

    @patch.object(QTimer, 'stop')
    @patch.object(QPropertyAnimation, 'stop')
    @patch.object(QPropertyAnimation, 'start')
    def test__show_scrollbar(self, mock_anim_start, mock_anim_stop, mock_timer_stop, scroll_bar_fixture):
        """Test _show_scrollbar."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture
        scroll_bar._opacity = 0.5 # Initial opacity

        scroll_bar._show_scrollbar()

        mock_timer_stop.assert_called_once()
        mock_anim_stop.assert_called_once()
        scroll_bar._fade_animation.setStartValue.assert_called_once_with(0.5)
        scroll_bar._fade_animation.setEndValue.assert_called_once_with(1.0)
        mock_anim_start.assert_called_once()

    @patch.object(QTimer, 'stop')
    @patch.object(QTimer, 'start')
    def test__schedule_hide(self, mock_timer_start, mock_timer_stop, scroll_bar_fixture):
        """Test _schedule_hide."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture

        scroll_bar._schedule_hide()

        mock_timer_stop.assert_called_once()
        mock_timer_start.assert_called_once_with(1000)

    @patch.object(QPropertyAnimation, 'stop')
    @patch.object(QPropertyAnimation, 'start')
    def test__on_hide_timeout(self, mock_anim_start, mock_anim_stop, scroll_bar_fixture):
        """Test _on_hide_timeout."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture
        scroll_bar._opacity = 1.0 # Initial opacity

        # Test not hovered and not pressed
        scroll_bar._is_hovered = False
        scroll_bar._is_pressed = False
        scroll_bar._on_hide_timeout()
        mock_anim_stop.assert_called_once()
        scroll_bar._fade_animation.setStartValue.assert_called_once_with(1.0)
        scroll_bar._fade_animation.setEndValue.assert_called_once_with(0.0)
        mock_anim_start.assert_called_once()

        # Test hovered
        mock_anim_stop.reset_mock()
        mock_anim_start.reset_mock()
        scroll_bar._is_hovered = True
        scroll_bar._is_pressed = False
        scroll_bar._on_hide_timeout()
        mock_anim_stop.assert_not_called()
        mock_anim_start.assert_not_called()

        # Test pressed
        mock_anim_stop.reset_mock()
        mock_anim_start.reset_mock()
        scroll_bar._is_hovered = False
        scroll_bar._is_pressed = True
        scroll_bar._on_hide_timeout()
        mock_anim_stop.assert_not_called()
        mock_anim_start.assert_not_called()

    @patch.object(FluentScrollBar, 'update')
    def test_set_theme(self, mock_update, scroll_bar_fixture):
        """Test set_theme."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture
        new_theme = {'color': 'red'}
        scroll_bar.set_theme(new_theme)
        assert scroll_bar._theme == new_theme
        mock_update.assert_called_once()

    def test_opacity_property(self, scroll_bar_fixture):
        """Test opacity property getter and setter."""
        scroll_bar, widgets, parent_widget = scroll_bar_fixture
        scroll_bar._opacity = 0.0 # Initial state

        with patch.object(FluentScrollBar, 'update') as mock_update:
            scroll_bar.opacity = 0.7
            assert scroll_bar._opacity == 0.7
            mock_update.assert_called_once()

            assert scroll_bar.opacity == 0.7 # Test getter


class TestFluentScrollViewer:
    """Unit tests for FluentScrollViewer."""

    @patch('components.layout.scroll_viewer.QScrollArea.__init__', return_value=None)
    @patch('components.layout.scroll_viewer.FluentControlBase.__init__', return_value=None)
    @patch.object(FluentScrollViewer, '_init_ui')
    @patch.object(FluentScrollViewer, '_setup_styling')
    @patch.object(FluentScrollViewer, '_setup_scrollbars')
    @patch.object(FluentScrollViewer, '_connect_signals')
    @patch.object(FluentScrollViewer, 'apply_theme')
    def test_init(self, mock_apply_theme, mock_connect_signals, mock_setup_scrollbars, mock_setup_styling, mock_init_ui, mock_control_base_init, mock_scroll_area_init, scroll_viewer_fixture):
        """Test initialization."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture

        # Re-initialize to use mocks
        mock_scroll_area_init.reset_mock()
        mock_control_base_init.reset_mock()
        mock_init_ui.reset_mock()
        mock_setup_styling.reset_mock()
        mock_setup_scrollbars.reset_mock()
        mock_connect_signals.reset_mock()
        mock_apply_theme.reset_mock()

        scroll_viewer.__init__(parent_widget)

        mock_scroll_area_init.assert_called_once_with(scroll_viewer, parent_widget) # QScrollArea takes self as first arg
        mock_control_base_init.assert_called_once_with(scroll_viewer, parent_widget) # FluentControlBase takes self as first arg

        assert scroll_viewer._smooth_scrolling is True
        assert scroll_viewer._auto_hide_scrollbars is True

        mock_init_ui.assert_called_once()
        mock_setup_styling.assert_called_once()
        mock_setup_scrollbars.assert_called_once()
        mock_connect_signals.assert_called_once()
        mock_apply_theme.assert_called_once()

    @patch.object(FluentScrollViewer, 'setFrameShape')
    @patch.object(FluentScrollViewer, 'setWidgetResizable')
    @patch.object(FluentScrollViewer, 'setHorizontalScrollBarPolicy')
    @patch.object(FluentScrollViewer, 'setVerticalScrollBarPolicy')
    @patch.object(FluentScrollViewer, 'setSizePolicy')
    def test__init_ui(self, mock_set_size_policy, mock_set_v_policy, mock_set_h_policy, mock_set_resizable, mock_set_frame_shape, scroll_viewer_fixture):
        """Test _init_ui sets basic properties."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture

        # Call the method directly
        mock_set_frame_shape.reset_mock()
        mock_set_resizable.reset_mock()
        mock_set_h_policy.reset_mock()
        mock_set_v_policy.reset_mock()
        mock_set_size_policy.reset_mock()

        scroll_viewer._init_ui()

        mock_set_frame_shape.assert_called_once_with(QFrame.Shape.NoFrame)
        mock_set_resizable.assert_called_once_with(True)
        mock_set_h_policy.assert_called_once_with(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        mock_set_v_policy.assert_called_once_with(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        mock_set_size_policy.assert_called_once_with(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    @patch.object(FluentScrollViewer, 'setStyleSheet')
    def test__setup_styling(self, mock_set_style_sheet, scroll_viewer_fixture):
        """Test _setup_styling sets the stylesheet."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture
        mock_set_style_sheet.reset_mock()

        scroll_viewer._setup_styling()

        mock_set_style_sheet.assert_called_once()
        # Cannot easily check the exact stylesheet content in a unit test

    @patch('components.layout.scroll_viewer.FluentScrollBar')
    @patch.object(FluentScrollViewer, 'setVerticalScrollBar')
    @patch.object(FluentScrollViewer, 'setHorizontalScrollBar')
    def test__setup_scrollbars(self, mock_set_h_scrollbar, mock_set_v_scrollbar, mock_scrollbar_class, scroll_viewer_fixture):
        """Test _setup_scrollbars creates and sets custom scrollbars."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture
        mock_v_scrollbar = Mock(spec=FluentScrollBar)
        mock_h_scrollbar = Mock(spec=FluentScrollBar)
        mock_scrollbar_class.side_effect = [mock_v_scrollbar, mock_h_scrollbar]

        # Test auto-hide enabled
        scroll_viewer._auto_hide_scrollbars = True
        mock_scrollbar_class.reset_mock()
        mock_set_v_scrollbar.reset_mock()
        mock_set_h_scrollbar.reset_mock()

        scroll_viewer._setup_scrollbars()

        mock_scrollbar_class.assert_has_calls([
            call(Qt.Orientation.Vertical, scroll_viewer),
            call(Qt.Orientation.Horizontal, scroll_viewer)
        ])
        assert hasattr(scroll_viewer, '_v_scrollbar')
        assert scroll_viewer._v_scrollbar == mock_v_scrollbar
        assert hasattr(scroll_viewer, '_h_scrollbar')
        assert scroll_viewer._h_scrollbar == mock_h_scrollbar
        mock_set_v_scrollbar.assert_called_once_with(mock_v_scrollbar)
        mock_set_h_scrollbar.assert_called_once_with(mock_h_scrollbar)

        # Test auto-hide disabled
        scroll_viewer._auto_hide_scrollbars = False
        # Remove existing custom scrollbars for this test
        if hasattr(scroll_viewer, '_v_scrollbar'): del scroll_viewer._v_scrollbar
        if hasattr(scroll_viewer, '_h_scrollbar'): del scroll_viewer._h_scrollbar
        mock_scrollbar_class.reset_mock()
        mock_set_v_scrollbar.reset_mock()
        mock_set_h_scrollbar.reset_mock()

        scroll_viewer._setup_scrollbars()

        mock_scrollbar_class.assert_not_called()
        mock_set_v_scrollbar.assert_not_called()
        mock_set_h_scrollbar.assert_not_called()
        assert not hasattr(scroll_viewer, '_v_scrollbar')
        assert not hasattr(scroll_viewer, '_h_scrollbar')

    @patch.object(FluentScrollViewer, 'verticalScrollBar')
    @patch.object(FluentScrollViewer, 'horizontalScrollBar')
    def test__connect_signals(self, mock_h_scrollbar_method, mock_v_scrollbar_method, scroll_viewer_fixture, mocker):
        """Test _connect_signals connects scrollbar valueChanged."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture

        # Mock custom scrollbars
        mock_v_scrollbar = Mock(spec=FluentScrollBar)
        mock_h_scrollbar = Mock(spec=FluentScrollBar)
        mock_v_scrollbar.valueChanged = mocker.Mock(spec=Qt.Signal)
        mock_h_scrollbar.valueChanged = mocker.Mock(spec=Qt.Signal)
        scroll_viewer._v_scrollbar = mock_v_scrollbar
        scroll_viewer._h_scrollbar = mock_h_scrollbar

        # Mock the methods that return the scrollbars to return our mocks
        mock_v_scrollbar_method.return_value = mock_v_scrollbar
        mock_h_scrollbar_method.return_value = mock_h_scrollbar

        # Call the method directly
        mock_v_scrollbar.valueChanged.connect.reset_mock()
        mock_h_scrollbar.valueChanged.connect.reset_mock()

        scroll_viewer._connect_signals()

        mock_v_scrollbar.valueChanged.connect.assert_called_once_with(scroll_viewer._on_scroll_changed)
        mock_h_scrollbar.valueChanged.connect.assert_called_once_with(scroll_viewer._on_scroll_changed)

        # Test case where custom scrollbars are not set (e.g., auto-hide disabled)
        del scroll_viewer._v_scrollbar
        del scroll_viewer._h_scrollbar
        mock_v_scrollbar.valueChanged.connect.reset_mock()
        mock_h_scrollbar.valueChanged.connect.reset_mock()

        scroll_viewer._connect_signals() # Should not raise error, but also not connect mocks
        mock_v_scrollbar.valueChanged.connect.assert_not_called()
        mock_h_scrollbar.valueChanged.connect.assert_not_called()


    @patch.object(FluentScrollViewer, 'verticalScrollBar')
    @patch.object(FluentScrollViewer, 'horizontalScrollBar')
    def test__on_scroll_changed(self, mock_h_scrollbar_method, mock_v_scrollbar_method, scroll_viewer_fixture, mocker):
        """Test _on_scroll_changed emits scroll_changed signal."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture
        mock_v_scrollbar = Mock(spec=QScrollBar)
        mock_h_scrollbar = Mock(spec=QScrollBar)
        mock_v_scrollbar_method.return_value = mock_v_scrollbar
        mock_h_scrollbar_method.return_value = mock_h_scrollbar

        mock_v_scrollbar.value.return_value = 50
        mock_h_scrollbar.value.return_value = 100

        mock_signal_emit = mocker.Mock()
        scroll_viewer.scroll_changed.emit = mock_signal_emit # Mock the signal emit

        scroll_viewer._on_scroll_changed()

        mock_signal_emit.assert_called_once_with(100, 50)

    @patch.object(FluentScrollViewer, '_animate_scroll_to')
    @patch.object(FluentScrollViewer, 'verticalScrollBar')
    def test_scroll_to_top(self, mock_v_scrollbar_method, mock_animate_scroll_to, scroll_viewer_fixture):
        """Test scroll_to_top."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture
        mock_v_scrollbar = Mock(spec=QScrollBar)
        mock_v_scrollbar_method.return_value = mock_v_scrollbar

        # Test animated and smooth scrolling enabled
        scroll_viewer._smooth_scrolling = True
        scroll_viewer.scroll_to_top(animated=True)
        mock_animate_scroll_to.assert_called_once_with(mock_v_scrollbar.value(), 0) # horizontal value is current

        # Test not animated
        mock_animate_scroll_to.reset_mock()
        mock_v_scrollbar.setValue.reset_mock()
        scroll_viewer.scroll_to_top(animated=False)
        mock_animate_scroll_to.assert_not_called()
        mock_v_scrollbar.setValue.assert_called_once_with(0)

        # Test smooth scrolling disabled
        mock_animate_scroll_to.reset_mock()
        mock_v_scrollbar.setValue.reset_mock()
        scroll_viewer._smooth_scrolling = False
        scroll_viewer.scroll_to_top(animated=True) # Animated=True but smooth=False
        mock_animate_scroll_to.assert_not_called()
        mock_v_scrollbar.setValue.assert_called_once_with(0)

    @patch.object(FluentScrollViewer, '_animate_scroll_to')
    @patch.object(FluentScrollViewer, 'verticalScrollBar')
    @patch.object(FluentScrollViewer, 'horizontalScrollBar')
    def test_scroll_to_bottom(self, mock_h_scrollbar_method, mock_v_scrollbar_method, mock_animate_scroll_to, scroll_viewer_fixture):
        """Test scroll_to_bottom."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture
        mock_v_scrollbar = Mock(spec=QScrollBar)
        mock_h_scrollbar = Mock(spec=QScrollBar)
        mock_v_scrollbar_method.return_value = mock_v_scrollbar
        mock_h_scrollbar_method.return_value = mock_h_scrollbar

        mock_v_scrollbar.maximum.return_value = 200
        mock_h_scrollbar.value.return_value = 50

        # Test animated and smooth scrolling enabled
        scroll_viewer._smooth_scrolling = True
        scroll_viewer.scroll_to_bottom(animated=True)
        mock_animate_scroll_to.assert_called_once_with(50, 200)

        # Test not animated
        mock_animate_scroll_to.reset_mock()
        mock_v_scrollbar.setValue.reset_mock()
        scroll_viewer.scroll_to_bottom(animated=False)
        mock_animate_scroll_to.assert_not_called()
        mock_v_scrollbar.setValue.assert_called_once_with(200)

        # Test smooth scrolling disabled
        mock_animate_scroll_to.reset_mock()
        mock_v_scrollbar.setValue.reset_mock()
        scroll_viewer._smooth_scrolling = False
        scroll_viewer.scroll_to_bottom(animated=True) # Animated=True but smooth=False
        mock_animate_scroll_to.assert_not_called()
        mock_v_scrollbar.setValue.assert_called_once_with(200)

    @patch.object(FluentScrollViewer, '_animate_scroll_to')
    @patch.object(FluentScrollViewer, 'verticalScrollBar')
    @patch.object(FluentScrollViewer, 'horizontalScrollBar')
    def test_scroll_to_position(self, mock_h_scrollbar_method, mock_v_scrollbar_method, mock_animate_scroll_to, scroll_viewer_fixture):
        """Test scroll_to_position."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture
        mock_v_scrollbar = Mock(spec=QScrollBar)
        mock_h_scrollbar = Mock(spec=QScrollBar)
        mock_v_scrollbar_method.return_value = mock_v_scrollbar
        mock_h_scrollbar_method.return_value = mock_h_scrollbar

        # Test animated and smooth scrolling enabled
        scroll_viewer._smooth_scrolling = True
        scroll_viewer.scroll_to_position(150, 250, animated=True)
        mock_animate_scroll_to.assert_called_once_with(150, 250)

        # Test not animated
        mock_animate_scroll_to.reset_mock()
        mock_h_scrollbar.setValue.reset_mock()
        mock_v_scrollbar.setValue.reset_mock()
        scroll_viewer.scroll_to_position(150, 250, animated=False)
        mock_animate_scroll_to.assert_not_called()
        mock_h_scrollbar.setValue.assert_called_once_with(150)
        mock_v_scrollbar.setValue.assert_called_once_with(250)

        # Test smooth scrolling disabled
        mock_animate_scroll_to.reset_mock()
        mock_h_scrollbar.setValue.reset_mock()
        mock_v_scrollbar.setValue.reset_mock()
        scroll_viewer._smooth_scrolling = False
        scroll_viewer.scroll_to_position(150, 250, animated=True) # Animated=True but smooth=False
        mock_animate_scroll_to.assert_not_called()
        mock_h_scrollbar.setValue.assert_called_once_with(150)
        mock_v_scrollbar.setValue.assert_called_once_with(250)

    @patch('components.layout.scroll_viewer.QPropertyAnimation')
    @patch.object(FluentScrollViewer, 'verticalScrollBar')
    @patch.object(FluentScrollViewer, 'horizontalScrollBar')
    def test__animate_scroll_to(self, mock_h_scrollbar_method, mock_v_scrollbar_method, mock_animation_class, scroll_viewer_fixture):
        """Test _animate_scroll_to creates and starts animations."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture
        mock_v_scrollbar = Mock(spec=QScrollBar)
        mock_h_scrollbar = Mock(spec=QScrollBar)
        mock_v_scrollbar_method.return_value = mock_v_scrollbar
        mock_h_scrollbar_method.return_value = mock_h_scrollbar

        mock_v_scrollbar.value.return_value = 10
        mock_h_scrollbar.value.return_value = 20

        mock_v_anim = Mock(spec=QPropertyAnimation)
        mock_h_anim = Mock(spec=QPropertyAnimation)
        mock_animation_class.side_effect = [mock_v_anim, mock_h_anim]

        scroll_viewer._animate_scroll_to(100, 200)

        # Check vertical animation
        mock_animation_class.assert_any_call(mock_v_scrollbar, QByteArray(b"value"))
        mock_v_anim.setDuration.assert_called_once_with(300)
        mock_v_anim.setEasingCurve.assert_called_once_with(QEasingCurve.Type.OutCubic)
        mock_v_anim.setStartValue.assert_called_once_with(10)
        mock_v_anim.setEndValue.assert_called_once_with(200)
        mock_v_anim.start.assert_called_once()
        assert hasattr(scroll_viewer, '_v_scroll_animation')
        assert scroll_viewer._v_scroll_animation == mock_v_anim

        # Check horizontal animation
        mock_animation_class.assert_any_call(mock_h_scrollbar, QByteArray(b"value"))
        mock_h_anim.setDuration.assert_called_once_with(300)
        mock_h_anim.setEasingCurve.assert_called_once_with(QEasingCurve.Type.OutCubic)
        mock_h_anim.setStartValue.assert_called_once_with(20)
        mock_h_anim.setEndValue.assert_called_once_with(100)
        mock_h_anim.start.assert_called_once()
        assert hasattr(scroll_viewer, '_h_scroll_animation')
        assert scroll_viewer._h_scroll_animation == mock_h_anim

        # Test stopping existing animations
        mock_animation_class.reset_mock()
        mock_v_anim.stop.reset_mock()
        mock_h_anim.stop.reset_mock()
        mock_v_anim_new = Mock(spec=QPropertyAnimation)
        mock_h_anim_new = Mock(spec=QPropertyAnimation)
        mock_animation_class.side_effect = [mock_v_anim_new, mock_h_anim_new]

        scroll_viewer._animate_scroll_to(50, 60)

        mock_v_anim.stop.assert_called_once() # Old animation stopped
        mock_h_anim.stop.assert_called_once() # Old animation stopped
        assert scroll_viewer._v_scroll_animation == mock_v_anim_new # New animation stored
        assert scroll_viewer._h_scroll_animation == mock_h_anim_new # New animation stored


    def test_set_smooth_scrolling(self, scroll_viewer_fixture):
        """Test set_smooth_scrolling."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture
        assert scroll_viewer._smooth_scrolling is True
        scroll_viewer.set_smooth_scrolling(False)
        assert scroll_viewer._smooth_scrolling is False
        scroll_viewer.set_smooth_scrolling(True)
        assert scroll_viewer._smooth_scrolling is True

    @patch.object(FluentScrollViewer, '_setup_scrollbars')
    def test_set_auto_hide_scrollbars(self, mock_setup_scrollbars, scroll_viewer_fixture):
        """Test set_auto_hide_scrollbars."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture
        assert scroll_viewer._auto_hide_scrollbars is True

        # Test disabling
        mock_setup_scrollbars.reset_mock()
        scroll_viewer.set_auto_hide_scrollbars(False)
        assert scroll_viewer._auto_hide_scrollbars is False
        mock_setup_scrollbars.assert_not_called() # Should not call setup when disabling

        # Test enabling
        mock_setup_scrollbars.reset_mock()
        scroll_viewer.set_auto_hide_scrollbars(True)
        assert scroll_viewer._auto_hide_scrollbars is True
        mock_setup_scrollbars.assert_called_once() # Should call setup when enabling

    @patch.object(FluentScrollViewer, 'verticalScrollBar')
    @patch.object(FluentScrollViewer, 'horizontalScrollBar')
    def test_get_scroll_position(self, mock_h_scrollbar_method, mock_v_scrollbar_method, scroll_viewer_fixture):
        """Test get_scroll_position."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture
        mock_v_scrollbar = Mock(spec=QScrollBar)
        mock_h_scrollbar = Mock(spec=QScrollBar)
        mock_v_scrollbar_method.return_value = mock_v_scrollbar
        mock_h_scrollbar_method.return_value = mock_h_scrollbar

        mock_v_scrollbar.value.return_value = 75
        mock_h_scrollbar.value.return_value = 125

        pos = scroll_viewer.get_scroll_position()
        assert pos == (125, 75)

    @patch.object(FluentScrollViewer, 'verticalScrollBar')
    @patch.object(FluentScrollViewer, 'horizontalScrollBar')
    def test_get_scroll_range(self, mock_h_scrollbar_method, mock_v_scrollbar_method, scroll_viewer_fixture):
        """Test get_scroll_range."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture
        mock_v_scrollbar = Mock(spec=QScrollBar)
        mock_h_scrollbar = Mock(spec=QScrollBar)
        mock_v_scrollbar_method.return_value = mock_v_scrollbar
        mock_h_scrollbar_method.return_value = mock_h_scrollbar

        mock_v_scrollbar.maximum.return_value = 300
        mock_h_scrollbar.maximum.return_value = 400

        rng = scroll_viewer.get_scroll_range()
        assert rng == (400, 300)

    @patch.object(FluentScrollViewer, 'setStyleSheet')
    @patch.object(FluentScrollBar, 'set_theme')
    @patch.object(FluentScrollViewer, 'get_current_theme') # Mock the base class method
    def test_apply_theme(self, mock_get_current_theme, mock_scrollbar_set_theme, mock_set_style_sheet, scroll_viewer_fixture, mocker):
        """Test apply_theme applies stylesheet and updates scrollbars."""
        scroll_viewer, widgets, parent_widget = scroll_viewer_fixture

        # Mock custom scrollbars being present
        mock_v_scrollbar = Mock(spec=FluentScrollBar)
        mock_h_scrollbar = Mock(spec=FluentScrollBar)
        scroll_viewer._v_scrollbar = mock_v_scrollbar
        scroll_viewer._h_scrollbar = mock_h_scrollbar

        # Mock theme data
        mock_theme = {
            'surface_background': '#111111',
            'scrollbar_thumb': '#222222',
            'scrollbar_thumb_hover': '#333333',
            'scrollbar_thumb_pressed': '#444444',
        }
        mock_get_current_theme.return_value = mock_theme

        mock_set_style_sheet.reset_mock()
        mock_scrollbar_set_theme.reset_mock()

        scroll_viewer.apply_theme()

        # Check if stylesheet was set (cannot check exact content easily)
        mock_set_style_sheet.assert_called_once()

        # Check if set_theme was called on custom scrollbars
        mock_scrollbar_set_theme.assert_has_calls([
            call(mock_theme),
            call(mock_theme)
        ])
        assert mock_scrollbar_set_theme.call_count == 2

        # Test case where custom scrollbars are not present
        del scroll_viewer._v_scrollbar
        del scroll_viewer._h_scrollbar
        mock_set_style_sheet.reset_mock()
        mock_scrollbar_set_theme.reset_mock()

        scroll_viewer.apply_theme()
        mock_set_style_sheet.assert_called_once() # Stylesheet still applied
        mock_scrollbar_set_theme.assert_not_called() # No custom scrollbars to update

        # Test case where get_current_theme returns non-dict
        mock_get_current_theme.return_value = None
        mock_set_style_sheet.reset_mock()
        mock_scrollbar_set_theme.reset_mock()

        scroll_viewer.apply_theme()
        mock_set_style_sheet.assert_not_called() # Stylesheet not applied if theme is invalid
        mock_scrollbar_set_theme.assert_not_called()
