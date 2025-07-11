import unittest
from unittest.mock import patch, MagicMock
import time
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QProgressBar, QLabel, QFrame, QDialog
from PySide6.QtCore import Qt, QTimer, Signal
from components.dialogs.progress_dialog import FluentProgressDialog, ProgressMode, show_progress_dialog, ProgressContext

# filepath: components/dialogs/test_progress_dialog.py


# Add the project root to the path if necessary for relative imports
# Assuming the test file is in components/dialogs/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from components.dialogs.base_dialog import ButtonRole # Needed for mocking button setup


class TestFluentProgressDialog(unittest.TestCase):
    """Test suite for FluentProgressDialog."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up for each test."""
        # Mock the base dialog's close_animated method
        with patch('components.dialogs.base_dialog.FluentBaseDialog.close_animated') as mock_close_animated:
             # Mock add_button to prevent actual button creation side effects during init tests
            with patch('components.dialogs.base_dialog.FluentBaseDialog.add_button') as mock_add_button:
                self.dialog = FluentProgressDialog()
                self.mock_close_animated = mock_close_animated
                self.mock_add_button = mock_add_button
        self.parent = QWidget()

    def tearDown(self):
        """Tear down after each test."""
        if self.dialog:
            # Ensure the dialog is closed to prevent lingering widgets
            try:
                self.dialog.close()
            except RuntimeError:
                pass # Dialog might already be deleted by accept/reject in tests
        if self.parent:
            self.parent.close()
        QApplication.processEvents() # Process events to clean up widgets

    def test_init_defaults(self):
        """Test the initialization with default parameters."""
        self.assertIsInstance(self.dialog, FluentProgressDialog)
        self.assertEqual(self.dialog.windowTitle(), "Please wait")
        self.assertEqual(self.dialog._message, "Processing...")
        self.assertTrue(self.dialog._cancelable)
        self.assertFalse(self.dialog._is_cancelled)
        self.assertEqual(self.dialog._progress_mode, ProgressMode.DETERMINATE)
        self.assertEqual(self.dialog._current_progress, 0)
        self.assertEqual(self.dialog._max_progress, 100)
        self.assertEqual(self.dialog._detail_text, "")
        self.assertEqual(self.dialog._subtask_text, "")
        self.assertIsNone(self.dialog._start_time)
        self.assertFalse(self.dialog._auto_close_on_complete)
        self.assertEqual(self.dialog._auto_close_delay, 2000)
        self.mock_add_button.assert_called_once_with("Cancel", ButtonRole.CANCEL, self.dialog._on_cancel_clicked)

    def test_init_custom(self):
        """Test initialization with custom parameters."""
        with patch('components.dialogs.base_dialog.FluentBaseDialog.close_animated'):
            with patch('components.dialogs.base_dialog.FluentBaseDialog.add_button') as mock_add_button:
                dialog = FluentProgressDialog(self.parent, "Custom Title", "Custom Message", cancelable=False)
                self.assertEqual(dialog.windowTitle(), "Custom Title")
                self.assertEqual(dialog._message, "Custom Message")
                self.assertFalse(dialog._cancelable)
                mock_add_button.assert_not_called() # No cancel button if not cancelable
                dialog.close() # Clean up

    def test_setup_content(self):
        """Test the _setup_content method."""
        # _setup_content is called in __init__, so check after init
        self.assertIsNotNone(self.dialog.message_label)
        self.assertIsInstance(self.dialog.message_label, QLabel)
        self.assertEqual(self.dialog.message_label.text(), self.dialog._message)

        self.assertIsNotNone(self.dialog.progress_bar)
        self.assertIsInstance(self.dialog.progress_bar, QProgressBar)
        self.assertEqual(self.dialog.progress_bar.minimum(), 0)
        self.assertEqual(self.dialog.progress_bar.maximum(), 100)
        self.assertEqual(self.dialog.progress_bar.value(), 0)

        self.assertIsNotNone(self.dialog.detail_label)
        self.assertIsInstance(self.dialog.detail_label, QLabel)
        self.assertFalse(self.dialog.detail_label.isVisible())

        self.assertIsNotNone(self.dialog.subtask_frame)
        self.assertIsInstance(self.dialog.subtask_frame, QFrame)
        self.assertFalse(self.dialog.subtask_frame.isVisible())

        self.assertIsNotNone(self.dialog.subtask_label)
        self.assertIsInstance(self.dialog.subtask_label, QLabel)

        self.assertIsNotNone(self.dialog.subtask_progress)
        self.assertIsInstance(self.dialog.subtask_progress, QProgressBar)

        self.assertIsNotNone(self.dialog.time_label)
        self.assertIsInstance(self.dialog.time_label, QLabel)
        self.assertFalse(self.dialog.time_label.isVisible())

    def test_setup_buttons_cancelable(self):
        """Test _setup_buttons when cancelable is True."""
        # Re-init with cancelable=True to ensure button setup is tested
        with patch('components.dialogs.base_dialog.FluentBaseDialog.close_animated'):
            with patch('components.dialogs.base_dialog.FluentBaseDialog.add_button') as mock_add_button:
                dialog = FluentProgressDialog(cancelable=True)
                mock_add_button.assert_called_once_with("Cancel", ButtonRole.CANCEL, dialog._on_cancel_clicked)
                self.assertIsNotNone(dialog.cancel_button)
                dialog.close()

    def test_setup_buttons_not_cancelable(self):
        """Test _setup_buttons when cancelable is False."""
        with patch('components.dialogs.base_dialog.FluentBaseDialog.close_animated'):
            with patch('components.dialogs.base_dialog.FluentBaseDialog.add_button') as mock_add_button:
                dialog = FluentProgressDialog(cancelable=False)
                mock_add_button.assert_not_called()
                self.assertFalse(hasattr(dialog, 'cancel_button'))
                dialog.close()

    def test_set_progress_mode_determinate(self):
        """Test setting progress mode to DETERMINATE."""
        self.dialog.set_progress_mode(ProgressMode.INDETERMINATE) # Start in a different mode
        self.dialog.set_progress_mode(ProgressMode.DETERMINATE)
        self.assertEqual(self.dialog._progress_mode, ProgressMode.DETERMINATE)
        self.assertEqual(self.dialog.progress_bar.minimum(), 0)
        self.assertEqual(self.dialog.progress_bar.maximum(), self.dialog._max_progress)
        self.assertFalse(self.dialog.subtask_frame.isVisible()) # Should remain hidden if not explicitly set to SUBTASK

    def test_set_progress_mode_indeterminate(self):
        """Test setting progress mode to INDETERMINATE."""
        self.dialog.set_progress_mode(ProgressMode.DETERMINATE) # Start in a different mode
        self.dialog.set_progress_mode(ProgressMode.INDETERMINATE)
        self.assertEqual(self.dialog._progress_mode, ProgressMode.INDETERMINATE)
        self.assertEqual(self.dialog.progress_bar.minimum(), 0)
        self.assertEqual(self.dialog.progress_bar.maximum(), 0) # Indeterminate range
        self.assertFalse(self.dialog.subtask_frame.isVisible()) # Should remain hidden

    def test_set_progress_mode_subtask(self):
        """Test setting progress mode to SUBTASK."""
        self.dialog.set_progress_mode(ProgressMode.DETERMINATE) # Start in a different mode
        self.dialog.set_progress_mode(ProgressMode.SUBTASK)
        self.assertEqual(self.dialog._progress_mode, ProgressMode.SUBTASK)
        self.assertTrue(self.dialog.subtask_frame.isVisible())

    @patch('components.dialogs.progress_dialog.FluentProgressDialog._on_completion')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog._update_time_estimation')
    def test_set_progress(self, mock_update_time, mock_on_completion):
        """Test setting progress value and detail."""
        progress_changed_spy = MagicMock()
        detail_changed_spy = MagicMock()
        self.dialog.progress_changed.connect(progress_changed_spy)
        self.dialog.detail_changed.connect(detail_changed_spy)

        self.dialog.set_progress(50, "Step 1/2")
        self.assertEqual(self.dialog._current_progress, 50)
        self.assertEqual(self.dialog.progress_bar.value(), 50)
        self.assertEqual(self.dialog._detail_text, "Step 1/2")
        self.assertEqual(self.dialog.detail_label.text(), "Step 1/2")
        self.assertTrue(self.dialog.detail_label.isVisible())
        progress_changed_spy.assert_called_once_with(50)
        detail_changed_spy.assert_called_once_with("Step 1/2")
        mock_update_time.assert_called_once()
        mock_on_completion.assert_not_called()

        # Test updating detail
        self.dialog.set_progress(75, "Step 2/2")
        self.assertEqual(self.dialog._current_progress, 75)
        self.assertEqual(self.dialog.progress_bar.value(), 75)
        self.assertEqual(self.dialog._detail_text, "Step 2/2")
        self.assertEqual(self.dialog.detail_label.text(), "Step 2/2")
        progress_changed_spy.assert_called_with(75)
        detail_changed_spy.assert_called_with("Step 2/2")
        self.assertEqual(progress_changed_spy.call_count, 2)
        self.assertEqual(detail_changed_spy.call_count, 2)

        # Test clearing detail
        self.dialog.set_progress(90, "")
        self.assertEqual(self.dialog._detail_text, "")
        self.assertFalse(self.dialog.detail_label.isVisible())
        detail_changed_spy.assert_called_with("")
        self.assertEqual(detail_changed_spy.call_count, 3)

        # Test completion
        self.dialog.set_progress(100)
        self.assertEqual(self.dialog._current_progress, 100)
        self.assertEqual(self.dialog.progress_bar.value(), 100)
        progress_changed_spy.assert_called_with(100)
        self.assertEqual(progress_changed_spy.call_count, 4)
        mock_on_completion.assert_called_once()

        # Test value clamping
        self.dialog.set_progress(150)
        self.assertEqual(self.dialog._current_progress, 100)
        self.dialog.set_progress(-10)
        self.assertEqual(self.dialog._current_progress, 0)


    def test_set_subtask_progress(self):
        """Test setting subtask progress."""
        self.dialog.set_subtask_progress(5, 10, "Processing file A")
        self.assertTrue(self.dialog.subtask_frame.isVisible())
        self.assertEqual(self.dialog.subtask_progress.minimum(), 0)
        self.assertEqual(self.dialog.subtask_progress.maximum(), 10)
        self.assertEqual(self.dialog.subtask_progress.value(), 5)
        self.assertEqual(self.dialog._subtask_text, "Processing file A")
        self.assertEqual(self.dialog.subtask_label.text(), "Processing file A")

        # Test updating subtask text
        self.dialog.set_subtask_progress(8, 10, "Processing file B")
        self.assertEqual(self.dialog._subtask_text, "Processing file B")
        self.assertEqual(self.dialog.subtask_label.text(), "Processing file B")

    def test_set_message(self):
        """Test setting the main message."""
        new_message = "New operation started..."
        self.dialog.set_message(new_message)
        self.assertEqual(self.dialog._message, new_message)
        self.assertEqual(self.dialog.message_label.text(), new_message)

    @patch('components.dialogs.progress_dialog.FluentProgressDialog.set_progress')
    def test_set_detail(self, mock_set_progress):
        """Test setting detail text."""
        self.dialog._current_progress = 30
        new_detail = "Loading data..."
        self.dialog.set_detail(new_detail)
        mock_set_progress.assert_called_once_with(30, new_detail)

    def test_set_range(self):
        """Test setting the progress range."""
        self.dialog.set_range(0, 200)
        self.assertEqual(self.dialog._max_progress, 200)
        self.assertEqual(self.dialog.progress_bar.minimum(), 0)
        self.assertEqual(self.dialog.progress_bar.maximum(), 200)

    @patch('time.time', return_value=1000.0)
    def test_start_timing(self, mock_time):
        """Test starting the time estimation."""
        self.dialog.start_timing()
        self.assertEqual(self.dialog._start_time, 1000.0)
        self.assertTrue(self.dialog.time_label.isVisible())

    @patch('time.time')
    def test_update_time_estimation(self, mock_time):
        """Test updating time estimation display."""
        mock_time.side_effect = [1000.0, 1010.0] # Start time, current time
        self.dialog._max_progress = 100
        self.dialog.start_timing() # Sets _start_time to 1000.0

        # Simulate progress
        self.dialog._current_progress = 10
        self.dialog._update_time_estimation() # Called by set_progress, but call directly for test
        # Elapsed = 10s, Progress = 10%, Estimated Total = 100s, Remaining = 90s
        self.assertEqual(self.dialog.time_label.text(), "About 90 seconds remaining")

        mock_time.side_effect = [1000.0, 1070.0] # Start time, current time
        self.dialog._current_progress = 50
        self.dialog._update_time_estimation()
        # Elapsed = 70s, Progress = 50%, Estimated Total = 140s, Remaining = 70s
        self.assertEqual(self.dialog.time_label.text(), "About 70 seconds remaining")

        mock_time.side_effect = [1000.0, 1000.0 + 60 * 5] # 5 minutes elapsed
        self.dialog._current_progress = 20
        self.dialog._update_time_estimation()
        # Elapsed = 300s, Progress = 20%, Estimated Total = 1500s, Remaining = 1200s (20 minutes)
        self.assertEqual(self.dialog.time_label.text(), "About 20 minutes remaining")

        mock_time.side_effect = [1000.0, 1000.0 + 3600 * 1.5] # 1.5 hours elapsed
        self.dialog._current_progress = 50
        self.dialog._update_time_estimation()
        # Elapsed = 5400s, Progress = 50%, Estimated Total = 10800s, Remaining = 5400s (1.5 hours)
        self.assertEqual(self.dialog.time_label.text(), "About 1 hour remaining") # Rounds down

        mock_time.side_effect = [1000.0, 1000.0 + 3600 * 2.5] # 2.5 hours elapsed
        self.dialog._current_progress = 50
        self.dialog._update_time_estimation()
        # Elapsed = 9000s, Progress = 50%, Estimated Total = 18000s, Remaining = 9000s (2.5 hours)
        self.assertEqual(self.dialog.time_label.text(), "About 2 hours remaining") # Rounds down

        # Test when progress is 0
        self.dialog._current_progress = 0
        self.dialog._update_time_estimation()
        # Label should not be updated if progress is 0
        # (The previous value might still be there, but the logic shouldn't run)
        # We can't easily assert the label text didn't change without more mocking,
        # but we can check the logic path.

    @patch('PySide6.QtCore.QTimer.singleShot')
    def test_on_completion_auto_close(self, mock_single_shot):
        """Test _on_completion with auto-close enabled."""
        self.dialog._auto_close_on_complete = True
        self.dialog._auto_close_delay = 1500
        self.dialog._on_completion()
        mock_single_shot.assert_called_once_with(1500, self.dialog.accept)
        # Cancel button text should not change if auto-closing

    def test_on_completion_no_auto_close(self):
        """Test _on_completion with auto-close disabled."""
        self.dialog._auto_close_on_complete = False
        # Ensure cancel button exists for this test
        with patch('components.dialogs.base_dialog.FluentBaseDialog.close_animated'):
             with patch('components.dialogs.base_dialog.FluentBaseDialog.add_button') as mock_add_button:
                dialog = FluentProgressDialog(cancelable=True)
                dialog.cancel_button = MagicMock() # Mock the button object
                dialog._on_completion()
                dialog.cancel_button.setText.assert_called_once_with("Close")
                dialog.close()

    @patch('components.dialogs.progress_dialog.FluentProgressDialog.reject')
    def test_on_cancel_clicked_not_complete(self, mock_reject):
        """Test _on_cancel_clicked when progress is not complete."""
        cancelled_spy = MagicMock()
        self.dialog.cancelled.connect(cancelled_spy)
        self.dialog._current_progress = 50
        self.dialog._max_progress = 100
        self.dialog._on_cancel_clicked()
        self.assertTrue(self.dialog._is_cancelled)
        cancelled_spy.assert_called_once()
        mock_reject.assert_called_once()
        self.mock_close_animated.assert_called_once_with(QDialog.DialogCode.Rejected)


    @patch('components.dialogs.progress_dialog.FluentProgressDialog.accept')
    def test_on_cancel_clicked_complete(self, mock_accept):
        """Test _on_cancel_clicked when progress is complete."""
        self.dialog._current_progress = 100
        self.dialog._max_progress = 100
        self.dialog._on_cancel_clicked()
        self.assertFalse(self.dialog._is_cancelled) # Should not be marked cancelled if complete
        mock_accept.assert_called_once()
        self.mock_close_animated.assert_called_once_with(QDialog.DialogCode.Accepted)


    def test_is_cancelled(self):
        """Test the is_cancelled method."""
        self.dialog._is_cancelled = False
        self.assertFalse(self.dialog.is_cancelled())
        self.dialog._is_cancelled = True
        self.assertTrue(self.dialog.is_cancelled())

    def test_set_auto_close_on_complete(self):
        """Test setting auto-close options."""
        self.dialog.set_auto_close_on_complete(True, 3000)
        self.assertTrue(self.dialog._auto_close_on_complete)
        self.assertEqual(self.dialog._auto_close_delay, 3000)

    def test_accept(self):
        """Test the accept method."""
        self.dialog.accept()
        self.mock_close_animated.assert_called_once_with(QDialog.DialogCode.Accepted)

    def test_reject(self):
        """Test the reject method."""
        self.dialog.reject()
        self.mock_close_animated.assert_called_once_with(QDialog.DialogCode.Rejected)

    @patch('components.dialogs.progress_dialog.FluentProgressDialog.show_animated')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.__init__', return_value=None)
    def test_show_progress_dialog_determinate(self, mock_init, mock_show_animated):
        """Test the show_progress_dialog helper function (determinate)."""
        mock_dialog = MagicMock(spec=FluentProgressDialog)
        mock_init.return_value = None # __init__ returns None
        mock_init.side_effect = lambda *args, **kwargs: setattr(mock_dialog, '__dict__', FluentProgressDialog(cancelable=True).__dict__) # Simulate init
        mock_dialog.set_progress_mode = MagicMock()

        with patch('components.dialogs.progress_dialog.FluentProgressDialog', return_value=mock_dialog):
            dialog = show_progress_dialog(self.parent, "Func Title", "Func Message", cancelable=False, indeterminate=False)

            mock_init.assert_called_once_with(self.parent, "Func Title", "Func Message", False)
            mock_dialog.set_progress_mode.assert_not_called() # Should not set mode if not indeterminate
            mock_show_animated.assert_called_once()
            self.assertIs(dialog, mock_dialog)

    @patch('components.dialogs.progress_dialog.FluentProgressDialog.show_animated')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.__init__', return_value=None)
    def test_show_progress_dialog_indeterminate(self, mock_init, mock_show_animated):
        """Test the show_progress_dialog helper function (indeterminate)."""
        mock_dialog = MagicMock(spec=FluentProgressDialog)
        mock_init.return_value = None # __init__ returns None
        mock_init.side_effect = lambda *args, **kwargs: setattr(mock_dialog, '__dict__', FluentProgressDialog(cancelable=True).__dict__) # Simulate init
        mock_dialog.set_progress_mode = MagicMock()

        with patch('components.dialogs.progress_dialog.FluentProgressDialog', return_value=mock_dialog):
            dialog = show_progress_dialog(self.parent, "Func Title", "Func Message", cancelable=True, indeterminate=True)

            mock_init.assert_called_once_with(self.parent, "Func Title", "Func Message", True)
            mock_dialog.set_progress_mode.assert_called_once_with(ProgressMode.INDETERMINATE)
            mock_show_animated.assert_called_once()
            self.assertIs(dialog, mock_dialog)

    @patch('components.dialogs.progress_dialog.FluentProgressDialog.show_animated')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.start_timing')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.__init__', return_value=None)
    def test_progress_context_enter(self, mock_init, mock_start_timing, mock_show_animated):
        """Test the ProgressContext __enter__ method."""
        mock_dialog = MagicMock(spec=FluentProgressDialog)
        mock_init.return_value = None # __init__ returns None
        mock_init.side_effect = lambda *args, **kwargs: setattr(mock_dialog, '__dict__', FluentProgressDialog(cancelable=True).__dict__) # Simulate init

        with patch('components.dialogs.progress_dialog.FluentProgressDialog', return_value=mock_dialog):
            with ProgressContext(self.parent, "Context Title", "Context Message", cancelable=False) as dialog:
                mock_init.assert_called_once_with(self.parent, "Context Title", "Context Message", False)
                mock_start_timing.assert_called_once()
                mock_show_animated.assert_called_once()
                self.assertIs(dialog, mock_dialog)

    @patch('PySide6.QtCore.QTimer.singleShot')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.set_progress')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.set_message')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.set_detail')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.accept')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.reject')
    def test_progress_context_exit_success(self, mock_reject, mock_accept, mock_set_detail, mock_set_message, mock_set_progress, mock_single_shot):
        """Test the ProgressContext __exit__ method on success."""
        mock_dialog = MagicMock(spec=FluentProgressDialog)
        mock_dialog.is_cancelled.return_value = False
        mock_dialog.accept = mock_accept
        mock_dialog.reject = mock_reject
        mock_dialog.set_progress = mock_set_progress
        mock_dialog.set_message = mock_set_message
        mock_dialog.set_detail = mock_set_detail

        context = ProgressContext(self.parent)
        context.dialog = mock_dialog # Replace the real dialog with the mock

        # Simulate exiting the context manager without an exception
        context.__exit__(None, None, None)

        mock_dialog.is_cancelled.assert_called_once()
        mock_set_progress.assert_called_once_with(100)
        mock_set_message.assert_not_called()
        mock_set_detail.assert_not_called()
        mock_single_shot.assert_called_once_with(500, mock_accept)
        mock_accept.assert_not_called() # Called by singleShot
        mock_reject.assert_not_called()

    @patch('PySide6.QtCore.QTimer.singleShot')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.set_progress')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.set_message')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.set_detail')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.accept')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.reject')
    def test_progress_context_exit_failure(self, mock_reject, mock_accept, mock_set_detail, mock_set_message, mock_set_progress, mock_single_shot):
        """Test the ProgressContext __exit__ method on failure."""
        mock_dialog = MagicMock(spec=FluentProgressDialog)
        mock_dialog.is_cancelled.return_value = False
        mock_dialog.accept = mock_accept
        mock_dialog.reject = mock_reject
        mock_dialog.set_progress = mock_set_progress
        mock_dialog.set_message = mock_set_message
        mock_dialog.set_detail = mock_set_detail

        context = ProgressContext(self.parent)
        context.dialog = mock_dialog # Replace the real dialog with the mock

        # Simulate exiting the context manager with an exception
        exc_type = ValueError
        exc_val = ValueError("Something went wrong")
        exc_tb = None
        context.__exit__(exc_type, exc_val, exc_tb)

        mock_dialog.is_cancelled.assert_called_once()
        mock_set_progress.assert_called_once_with(100) # Still sets to 100 on error
        mock_set_message.assert_called_once_with("An error occurred.")
        mock_set_detail.assert_called_once_with("Something went wrong")
        mock_single_shot.assert_called_once_with(2000, mock_reject)
        mock_accept.assert_not_called()
        mock_reject.assert_not_called() # Called by singleShot

    @patch('PySide6.QtCore.QTimer.singleShot')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.set_progress')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.set_message')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.set_detail')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.accept')
    @patch('components.dialogs.progress_dialog.FluentProgressDialog.reject')
    def test_progress_context_exit_cancelled(self, mock_reject, mock_accept, mock_set_detail, mock_set_message, mock_set_progress, mock_single_shot):
        """Test the ProgressContext __exit__ method when cancelled."""
        mock_dialog = MagicMock(spec=FluentProgressDialog)
        mock_dialog.is_cancelled.return_value = True
        mock_dialog.accept = mock_accept
        mock_dialog.reject = mock_reject
        mock_dialog.set_progress = mock_set_progress
        mock_dialog.set_message = mock_set_message
        mock_dialog.set_detail = mock_set_detail

        context = ProgressContext(self.parent)
        context.dialog = mock_dialog # Replace the real dialog with the mock

        # Simulate exiting the context manager after cancellation
        context.__exit__(None, None, None)

        mock_dialog.is_cancelled.assert_called_once()
        mock_set_progress.assert_not_called() # Should not set progress if cancelled
        mock_set_message.assert_not_called()
        mock_set_detail.assert_not_called()
        mock_single_shot.assert_not_called()
        mock_accept.assert_not_called()
        mock_reject.assert_not_called() # Reject is handled by _on_cancel_clicked


if __name__ == '__main__':
    unittest.main()