import sys
import os
import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QRect, QSize, Qt, QTimer, QMargins, QPropertyAnimation, QEasingCurve, QByteArray
from PySide6.QtGui import QResizeEvent
from components.layout.layout_base import FluentLayoutBase
from core.theme import theme_manager

# filepath: d:\Project\simple-fluent-widget\tests\components\layout\test_layout_base.py


# Add the project root directory to the path for relative import
# Assuming the test file is in tests/components/layout/
# and the source is in components/layout/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Import the class to test
# Assuming theme_manager is in core/theme.py


@pytest.fixture(scope="session")
def app_fixture():
    """Provides a QApplication instance for the test session."""
    if not QApplication.instance():
        return QApplication(sys.argv)
    return QApplication.instance()

@pytest.fixture(scope="function")
def layout_base_fixture(app_fixture, request):
    """Provides a FluentLayoutBase instance and a list to track widgets for cleanup."""
    # Create a parent widget for the layout
    parent_widget = QWidget()
    # FluentLayoutBase is a QWidget subclass, not a QLayout subclass
    layout_base_widget = FluentLayoutBase(parent_widget)
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

    return layout_base_widget, widgets_to_clean, parent_widget

class TestFluentLayoutBase:
    """Unit tests for FluentLayoutBase using pytest."""

    @patch.object(FluentLayoutBase, '_apply_layout_theme')
    @patch.object(FluentLayoutBase, '_update_current_breakpoint')
    def test_init(self, mock_update_breakpoint, mock_apply_theme, layout_base_fixture):
        """Test initialization."""
        layout_base, widgets, parent_widget = layout_base_fixture
        assert isinstance(layout_base, FluentLayoutBase)
        assert layout_base.parent() == parent_widget

        # Check default properties
        assert layout_base._spacing == 8
        assert layout_base._padding == QMargins(0, 0, 0, 0)
        assert layout_base._responsive_enabled is True
        assert layout_base._layout_animations_enabled is True
        assert layout_base._current_breakpoint == 'xs' # Initial value before update_current_breakpoint
        assert layout_base._animation_duration == 200
        assert layout_base._animation_easing == QEasingCurve.Type.OutCubic
        assert isinstance(layout_base._layout_update_timer, QTimer)
        assert layout_base._layout_update_timer.isSingleShot()
        assert layout_base._layout_update_timer.interval() == 16
        assert not hasattr(layout_base, '_needs_layout_update') # Should not exist initially

        # Check setup calls
        mock_apply_theme.assert_called_once()
        mock_update_breakpoint.assert_called_once()

    @patch.object(FluentLayoutBase, '_apply_custom_theme_tokens')
    def test__apply_layout_theme(self, mock_apply_custom_tokens, layout_base_fixture, mocker):
        """Test _apply_layout_theme applies theme and calls custom method."""
        layout_base, widgets, parent_widget = layout_base_fixture

        # Mock theme_manager.get_color
        mock_get_color = mocker.patch.object(theme_manager, 'get_color')
        mock_color = Mock()
        mock_color.name.return_value = "#123456"
        mock_get_color.return_value = mock_color

        # Mock theme_manager.theme_changed signal connection (already done in init, just verify)
        # This is harder to test directly without mocking the signal itself before init

        # Call the method
        layout_base._apply_layout_theme()

        # Check if custom theme tokens method was called
        mock_apply_custom_tokens.assert_called_once()
        # Check if animation duration was updated (based on default tokens)
        assert layout_base._animation_duration == 200 # Default value from tokens

    @patch.object(FluentLayoutBase, 'resizeEvent') # Patch super call
    @patch.object(FluentLayoutBase, '_update_current_breakpoint')
    @patch.object(FluentLayoutBase, '_on_breakpoint_changed')
    @patch.object(QTimer, 'start') # Patch timer start
    @patch.object(FluentLayoutBase, '_process_layout_update') # Patch direct call
    def test_resizeEvent(self, mock_process_layout_update, mock_timer_start, mock_on_breakpoint_changed, mock_update_breakpoint, mock_super_resize, layout_base_fixture, mocker):
        """Test resizeEvent triggers responsive logic and layout update."""
        layout_base, widgets, parent_widget = layout_base_fixture
        event = Mock(spec=QResizeEvent)

        # Mock initial breakpoint
        layout_base._current_breakpoint = 'md'
        mock_update_breakpoint.side_effect = lambda: setattr(layout_base, '_current_breakpoint', 'lg') # Simulate breakpoint change

        # Test responsive enabled, animations enabled
        layout_base.set_responsive_enabled(True)
        layout_base.set_layout_animations_enabled(True)
        mock_update_breakpoint.reset_mock() # Reset call count from init
        mock_on_breakpoint_changed.reset_mock()
        mock_timer_start.reset_mock()
        mock_process_layout_update.reset_mock()

        layout_base.resizeEvent(event)

        mock_super_resize.assert_called_once_with(event)
        mock_update_breakpoint.assert_called_once()
        mock_on_breakpoint_changed.assert_called_once_with('md', 'lg')
        mock_timer_start.assert_called_once()
        mock_process_layout_update.assert_not_called() # Timer should handle it

        # Test responsive enabled, animations disabled
        layout_base.set_responsive_enabled(True)
        layout_base.set_layout_animations_enabled(False)
        layout_base._current_breakpoint = 'lg' # Reset breakpoint for next test
        mock_update_breakpoint.side_effect = lambda: setattr(layout_base, '_current_breakpoint', 'xl') # Simulate breakpoint change
        mock_update_breakpoint.reset_mock()
        mock_on_breakpoint_changed.reset_mock()
        mock_timer_start.reset_mock()
        mock_process_layout_update.reset_mock()

        layout_base.resizeEvent(event)

        mock_super_resize.assert_called_once_with(event) # Called again
        mock_update_breakpoint.assert_called_once()
        mock_on_breakpoint_changed.assert_called_once_with('lg', 'xl')
        mock_timer_start.assert_not_called()
        mock_process_layout_update.assert_called_once() # Should process directly

        # Test responsive disabled
        layout_base.set_responsive_enabled(False)
        layout_base.set_layout_animations_enabled(True) # Animations enabled, but responsive off
        layout_base._current_breakpoint = 'xl' # Reset breakpoint
        mock_update_breakpoint.side_effect = lambda: setattr(layout_base, '_current_breakpoint', 'xxl') # Simulate breakpoint change
        mock_update_breakpoint.reset_mock()
        mock_on_breakpoint_changed.reset_mock()
        mock_timer_start.reset_mock()
        mock_process_layout_update.reset_mock()

        layout_base.resizeEvent(event)

        mock_super_resize.assert_called_once_with(event) # Called again
        mock_update_breakpoint.assert_not_called() # Responsive off, no breakpoint update
        mock_on_breakpoint_changed.assert_not_called()
        mock_timer_start.assert_called_once() # Timer still starts if animations enabled
        mock_process_layout_update.assert_not_called()

    @patch.object(FluentLayoutBase, 'width', return_value=1000) # Mock widget width
    def test__update_current_breakpoint(self, mock_width, layout_base_fixture):
        """Test _update_current_breakpoint logic."""
        layout_base, widgets, parent_widget = layout_base_fixture

        # Default breakpoints: {'xs': 0, 'sm': 576, 'md': 768, 'lg': 992, 'xl': 1200, 'xxl': 1400}

        mock_width.return_value = 300 # xs
        layout_base._update_current_breakpoint()
        assert layout_base._current_breakpoint == 'xs'

        mock_width.return_value = 600 # sm
        layout_base._update_current_breakpoint()
        assert layout_base._current_breakpoint == 'sm'

        mock_width.return_value = 800 # md
        layout_base._update_current_breakpoint()
        assert layout_base._current_breakpoint == 'md'

        mock_width.return_value = 1000 # lg
        layout_base._update_current_breakpoint()
        assert layout_base._current_breakpoint == 'lg'

        mock_width.return_value = 1300 # xl
        layout_base._update_current_breakpoint()
        assert layout_base._current_breakpoint == 'xl'

        mock_width.return_value = 1500 # xxl
        layout_base._update_current_breakpoint()
        assert layout_base._current_breakpoint == 'xxl'

        # Test with custom breakpoints
        layout_base.set_breakpoints({'small': 0, 'large': 700})
        mock_width.return_value = 500 # small
        layout_base._update_current_breakpoint()
        assert layout_base._current_breakpoint == 'small'

        mock_width.return_value = 800 # large
        layout_base._update_current_breakpoint()
        assert layout_base._current_breakpoint == 'large'

    @patch.object(FluentLayoutBase, '_perform_layout_update')
    def test__process_layout_update(self, mock_perform_update, layout_base_fixture):
        """Test _process_layout_update calls perform and resets flag."""
        layout_base, widgets, parent_widget = layout_base_fixture

        # Case 1: _needs_layout_update is True
        layout_base._needs_layout_update = True
        layout_base._process_layout_update()
        mock_perform_update.assert_called_once()
        assert layout_base._needs_layout_update is False

        # Case 2: _needs_layout_update is False
        mock_perform_update.reset_mock()
        layout_base._needs_layout_update = False
        layout_base._process_layout_update()
        mock_perform_update.assert_not_called()
        assert layout_base._needs_layout_update is False # Remains False

        # Case 3: _needs_layout_update is not set (initial state)
        del layout_base._needs_layout_update # Remove the attribute
        mock_perform_update.reset_mock()
        layout_base._process_layout_update()
        mock_perform_update.assert_not_called()
        assert not hasattr(layout_base, '_needs_layout_update') # Attribute not created

    @patch.object(QTimer, 'start')
    @patch.object(FluentLayoutBase, '_process_layout_update')
    def test_request_layout_update(self, mock_process_layout_update, mock_timer_start, layout_base_fixture):
        """Test request_layout_update sets flag and triggers update."""
        layout_base, widgets, parent_widget = layout_base_fixture

        # Test animations enabled
        layout_base.set_layout_animations_enabled(True)
        mock_timer_start.reset_mock()
        mock_process_layout_update.reset_mock()
        assert not hasattr(layout_base, '_needs_layout_update')

        layout_base.request_layout_update()

        assert layout_base._needs_layout_update is True
        mock_timer_start.assert_called_once()
        mock_process_layout_update.assert_not_called()

        # Test animations disabled
        layout_base.set_layout_animations_enabled(False)
        mock_timer_start.reset_mock()
        mock_process_layout_update.reset_mock()
        layout_base._needs_layout_update = False # Reset flag

        layout_base.request_layout_update()

        assert layout_base._needs_layout_update is True
        mock_timer_start.assert_not_called()
        mock_process_layout_update.assert_called_once()

    def test__perform_layout_update(self, layout_base_fixture, mocker):
        """Test _perform_layout_update emits layout_changed signal."""
        layout_base, widgets, parent_widget = layout_base_fixture
        mock_signal = mocker.Mock()
        layout_base.layout_changed.connect(mock_signal)

        layout_base._perform_layout_update()

        mock_signal.emit.assert_called_once()

    @patch.object(FluentLayoutBase, 'request_layout_update')
    def test_set_spacing(self, mock_request_update, layout_base_fixture):
        """Test set_spacing updates value and requests layout update."""
        layout_base, widgets, parent_widget = layout_base_fixture
        assert layout_base._spacing == 8

        layout_base.set_spacing(16)
        assert layout_base._spacing == 16
        mock_request_update.assert_called_once()

        # Setting same value should not request update
        mock_request_update.reset_mock()
        layout_base.set_spacing(16)
        assert layout_base._spacing == 16
        mock_request_update.assert_not_called()

    def test_get_spacing(self, layout_base_fixture):
        """Test get_spacing returns current value."""
        layout_base, widgets, parent_widget = layout_base_fixture
        layout_base._spacing = 20
        assert layout_base.get_spacing() == 20

    @patch.object(FluentLayoutBase, 'request_layout_update')
    def test_set_padding(self, mock_request_update, layout_base_fixture):
        """Test set_padding updates value and requests layout update."""
        layout_base, widgets, parent_widget = layout_base_fixture
        assert layout_base._padding == QMargins(0, 0, 0, 0)

        # Test setting all sides
        layout_base.set_padding(10)
        assert layout_base._padding == QMargins(10, 10, 10, 10)
        mock_request_update.assert_called_once()

        # Test setting left, top, right, bottom
        mock_request_update.reset_mock()
        layout_base.set_padding(5, 10, 15, 20)
        assert layout_base._padding == QMargins(5, 10, 15, 20)
        mock_request_update.assert_called_once()

        # Test setting left, top, right
        mock_request_update.reset_mock()
        layout_base.set_padding(2, 4, 6)
        assert layout_base._padding == QMargins(2, 4, 6, 4) # bottom should be same as top
        mock_request_update.assert_called_once()

        # Test setting left, top
        mock_request_update.reset_mock()
        layout_base.set_padding(1, 2)
        assert layout_base._padding == QMargins(1, 2, 1, 2) # right same as left, bottom same as top
        mock_request_update.assert_called_once()

        # Setting same value should not request update
        mock_request_update.reset_mock()
        layout_base.set_padding(1, 2, 1, 2)
        assert layout_base._padding == QMargins(1, 2, 1, 2)
        mock_request_update.assert_not_called()

    def test_get_padding(self, layout_base_fixture):
        """Test get_padding returns current value."""
        layout_base, widgets, parent_widget = layout_base_fixture
        layout_base._padding = QMargins(1, 2, 3, 4)
        assert layout_base.get_padding() == QMargins(1, 2, 3, 4)

    def test_set_responsive_enabled(self, layout_base_fixture):
        """Test set_responsive_enabled updates value."""
        layout_base, widgets, parent_widget = layout_base_fixture
        assert layout_base.is_responsive_enabled() is True
        layout_base.set_responsive_enabled(False)
        assert layout_base.is_responsive_enabled() is False
        layout_base.set_responsive_enabled(True)
        assert layout_base.is_responsive_enabled() is True

    def test_is_responsive_enabled(self, layout_base_fixture):
        """Test is_responsive_enabled returns current value."""
        layout_base, widgets, parent_widget = layout_base_fixture
        layout_base._responsive_enabled = False
        assert layout_base.is_responsive_enabled() is False

    @patch.object(FluentLayoutBase, '_update_current_breakpoint')
    def test_set_breakpoints(self, mock_update_breakpoint, layout_base_fixture):
        """Test set_breakpoints updates value and triggers breakpoint update."""
        layout_base, widgets, parent_widget = layout_base_fixture
        new_breakpoints = {'a': 0, 'b': 100}
        layout_base.set_breakpoints(new_breakpoints)
        assert layout_base._breakpoints == new_breakpoints
        mock_update_breakpoint.assert_called_once()

        # Check that a copy is stored
        new_breakpoints['c'] = 200
        assert layout_base._breakpoints != new_breakpoints

    def test_get_breakpoints(self, layout_base_fixture):
        """Test get_breakpoints returns a copy of current value."""
        layout_base, widgets, parent_widget = layout_base_fixture
        breakpoints = layout_base.get_breakpoints()
        assert breakpoints == layout_base._breakpoints
        assert breakpoints is not layout_base._breakpoints # Should be a copy

    def test_get_current_breakpoint(self, layout_base_fixture):
        """Test get_current_breakpoint returns current value."""
        layout_base, widgets, parent_widget = layout_base_fixture
        layout_base._current_breakpoint = 'test_bp'
        assert layout_base.get_current_breakpoint() == 'test_bp'

    def test_set_layout_animations_enabled(self, layout_base_fixture):
        """Test set_layout_animations_enabled updates value."""
        layout_base, widgets, parent_widget = layout_base_fixture
        assert layout_base._layout_animations_enabled is True
        layout_base.set_layout_animations_enabled(False)
        assert layout_base._layout_animations_enabled is False
        layout_base.set_layout_animations_enabled(True)
        assert layout_base._layout_animations_enabled is True

    @patch('components.layout.layout_base.QPropertyAnimation')
    def test_animate_layout_change(self, mock_animation_class, layout_base_fixture, mocker):
        """Test animate_layout_change creates and starts animation."""
        layout_base, widgets, parent_widget = layout_base_fixture
        mock_animation = Mock(spec=QPropertyAnimation)
        mock_animation.finished = Mock(spec=Qt.Signal) # Mock the finished signal
        mock_animation_class.return_value = mock_animation

        mock_finished_callback = mocker.Mock()
        mock_layout_animating_signal = mocker.Mock()
        layout_base.layout_animating.connect(mock_layout_animating_signal)

        # Test animation enabled
        layout_base.set_layout_animations_enabled(True)
        layout_base.animate_layout_change(
            "test_anim", "geometry", QRect(0, 0, 10, 10), QRect(10, 10, 20, 20),
            mock_finished_callback
        )

        mock_animation_class.assert_called_once_with(layout_base, QByteArray(b'geometry'))
        mock_animation.setDuration.assert_called_once_with(layout_base._animation_duration)
        mock_animation.setEasingCurve.assert_called_once_with(layout_base._animation_easing)
        mock_animation.setStartValue.assert_called_once_with(QRect(0, 0, 10, 10))
        mock_animation.setEndValue.assert_called_once_with(QRect(10, 10, 20, 20))
        mock_animation.finished.connect.assert_any_call(mock_finished_callback)
        mock_animation.finished.connect.assert_any_call(mocker.ANY) # Check for lambda connection
        mock_animation.start.assert_called_once()
        assert "test_anim" in layout_base._layout_animations
        assert layout_base._layout_animations["test_anim"] == mock_animation
        mock_layout_animating_signal.emit.assert_called_once_with(True) # Signal emitted at start

        # Simulate animation finished to check the second signal emit
        mock_animation.finished.emit()
        assert mock_layout_animating_signal.emit.call_count == 2
        mock_layout_animating_signal.emit.assert_called_with(False)

        # Test stopping existing animation
        mock_animation_class.reset_mock()
        mock_animation.stop.reset_mock()
        mock_layout_animating_signal.reset_mock()

        layout_base.animate_layout_change(
            "test_anim", "opacity", 0, 1
        )
        mock_animation.stop.assert_called_once() # Old animation stopped
        mock_animation_class.assert_called_once_with(layout_base, QByteArray(b'opacity')) # New animation created
        assert "test_anim" in layout_base._layout_animations # Key still exists
        assert layout_base._layout_animations["test_anim"] != mock_animation # Value is the new animation
        mock_layout_animating_signal.emit.assert_called_once_with(True)

        # Test animation disabled
        layout_base.set_layout_animations_enabled(False)
        mock_animation_class.reset_mock()
        mock_finished_callback.reset_mock()
        mock_layout_animating_signal.reset_mock()

        layout_base.animate_layout_change(
            "another_anim", "pos", QRect(0, 0, 10, 10), QRect(10, 10, 20, 20),
            mock_finished_callback
        )
        mock_animation_class.assert_not_called()
        mock_finished_callback.assert_called_once() # Callback should still be called
        mock_layout_animating_signal.assert_not_called() # Signals should not be emitted

    # Test for FluentContainerBase (briefly, as it's not the main focus)
    # This class inherits FluentLayoutBase, so its base functionality is covered above.
    # We'll add a basic test for its init and a key method.
    @patch.object(FluentLayoutBase, '__init__', return_value=None) # Mock parent init
    @patch.object(FluentLayoutBase, '_setup_layout_base') # Mock parent setup
    @patch('components.layout.layout_base.FluentContainerBase._apply_container_styling') # Patch its own styling method
    def test_fluentcontainerbase_init(self, mock_apply_styling, mock_setup_layout_base, mock_super_init, layout_base_fixture):
        """Test FluentContainerBase initialization."""
        # We need a QFrame subclass to test setFrameStyle, but the fixture provides QWidget.
        # Let's create a simple mock class that inherits QFrame and FluentContainerBase
        class MockContainer(QFrame, FluentLayoutBase): # Inherit QFrame first
             def __init__(self, parent=None):
                 # Call FluentLayoutBase init which calls super().__init__(parent) (QWidget)
                 # and _setup_layout_base
                 FluentLayoutBase.__init__(self, parent)
                 # Call QFrame init explicitly if needed, but FluentLayoutBase init should handle parent
                 # QFrame.__init__(self, parent) # Not strictly necessary if FluentLayoutBase handles parent

             # Mock abstract methods from FluentLayoutBase if they were not stubs
             def _apply_custom_theme_tokens(self, tokens): pass
             def _on_breakpoint_changed(self, old, new): pass
             def _perform_layout_update(self): pass
             def _apply_layout_strategy(self, strategy): pass

             # Mock methods called by FluentContainerBase init
             def _setup_container_base(self):
                 # Simulate the logic from the actual _setup_container_base
                 if hasattr(self, 'setFrameStyle') and isinstance(self, QFrame):
                     self.setFrameStyle(QFrame.Shape.NoFrame)
                 self._apply_container_styling()

             def _apply_container_styling(self):
                 # Mock this method as it's patched
                 pass


        # Create an instance of the mock container
        parent_widget = QWidget()
        mock_container = MockContainer(parent_widget)

        # Check if parent init was called
        mock_super_init.assert_called_once_with(parent_widget)
        # Check if base layout setup was called
        mock_setup_layout_base.assert_called_once()
        # Check if container-specific setup was called (implicitly via init)
        # Check if styling was applied
        mock_apply_styling.assert_called_once()

        # Check default container properties
        assert mock_container._clickable is False
        assert mock_container._elevated is False
        assert mock_container._elevation_level == 1
        assert mock_container._corner_radius == 8
        assert mock_container._header_widget is None
        assert mock_container._content_widget is None
        assert mock_container._footer_widget is None

        # Clean up
        parent_widget.deleteLater()
        QApplication.processEvents()

    @patch('components.layout.layout_base.FluentContainerBase._apply_container_styling')
    def test_fluentcontainerbase_set_clickable(self, mock_apply_styling, layout_base_fixture):
        """Test FluentContainerBase set_clickable."""
        # Use the fixture, which provides FluentLayoutBase (not QFrame), but we can still test the property and styling call
        layout_base, widgets, parent_widget = layout_base_fixture
        # Cast to FluentContainerBase to access its methods/properties
        container = layout_base # Assuming the fixture provides a FluentContainerBase or similar

        # Mock the _setup_container_base call in init
        with patch.object(container, '_setup_container_base'):
             container.__init__(parent_widget) # Re-init to ensure clean state for this test

        mock_apply_styling.reset_mock() # Reset mock after init calls

        assert container._clickable is False
        container.set_clickable(True)
        assert container._clickable is True
        mock_apply_styling.assert_called_once()

        mock_apply_styling.reset_mock()
        container.set_clickable(True) # Set same value
        assert container._clickable is True
        mock_apply_styling.assert_not_called()

        mock_apply_styling.reset_mock()
        container.set_clickable(False)
        assert container._clickable is False
        mock_apply_styling.assert_called_once()

    # Test for FluentAdaptiveLayoutBase (briefly)
    # This class inherits FluentLayoutBase, so its base functionality is covered.
    # Test its init and breakpoint change handling.
    @patch.object(FluentLayoutBase, '__init__', return_value=None) # Mock parent init
    @patch.object(FluentLayoutBase, '_setup_layout_base') # Mock parent setup
    def test_fluentadaptivelayoutbase_init(self, mock_setup_layout_base, mock_super_init, layout_base_fixture):
        """Test FluentAdaptiveLayoutBase initialization."""
        # Use the fixture, which provides FluentLayoutBase
        layout_base, widgets, parent_widget = layout_base_fixture
        # Cast to FluentAdaptiveLayoutBase to access its methods/properties
        adaptive_layout = layout_base # Assuming the fixture provides a FluentAdaptiveLayoutBase or similar

        # Mock the _setup_layout_base call in init
        with patch.object(adaptive_layout, '_setup_layout_base'):
             adaptive_layout.__init__(parent_widget) # Re-init

        mock_super_init.assert_called_once_with(parent_widget)
        mock_setup_layout_base.assert_called_once()

        # Check default adaptive properties
        assert adaptive_layout._layout_strategies == {}
        assert adaptive_layout._transition_animations == []

    @patch.object(FluentLayoutBase, '_on_breakpoint_changed') # Patch super call
    @patch('components.layout.layout_base.FluentAdaptiveLayoutBase._apply_layout_strategy')
    def test_fluentadaptivelayoutbase_on_breakpoint_changed(self, mock_apply_strategy, mock_super_on_breakpoint_changed, layout_base_fixture):
        """Test FluentAdaptiveLayoutBase _on_breakpoint_changed calls apply_layout_strategy."""
        # Use the fixture, which provides FluentLayoutBase
        layout_base, widgets, parent_widget = layout_base_fixture
        # Cast to FluentAdaptiveLayoutBase
        adaptive_layout = layout_base # Assuming the fixture provides a FluentAdaptiveLayoutBase or similar

        # Mock the _setup_layout_base call in init
        with patch.object(adaptive_layout, '_setup_layout_base'):
             adaptive_layout.__init__(parent_widget) # Re-init

        mock_super_on_breakpoint_changed.reset_mock() # Reset mock after init calls
        mock_apply_strategy.reset_mock()

        # Add a strategy
        test_strategy = {"key": "value"}
        adaptive_layout.add_layout_strategy("new_bp", test_strategy)

        # Simulate breakpoint change to the new breakpoint
        adaptive_layout._on_breakpoint_changed("old_bp", "new_bp")

        mock_super_on_breakpoint_changed.assert_called_once_with("old_bp", "new_bp")
        mock_apply_strategy.assert_called_once_with(test_strategy)

        # Simulate breakpoint change to a breakpoint without a strategy
        mock_super_on_breakpoint_changed.reset_mock()
        mock_apply_strategy.reset_mock()
        adaptive_layout._on_breakpoint_changed("new_bp", "another_bp")

        mock_super_on_breakpoint_changed.assert_called_once_with("new_bp", "another_bp")
        mock_apply_strategy.assert_not_called()
