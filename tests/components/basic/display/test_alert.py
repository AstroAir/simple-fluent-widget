import pytest
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtTest import QTest

from components.basic.display.alert import (
    EnhancedFluentAlert,
    EnhancedFluentNotification,
    FluentMessageBar,
    AlertType,
    AlertPriority,
    AlertObjectPool,
    AlertManager,
    alert_manager,  # global instance
    create_info_alert,
    create_success_alert,
    create_warning_alert,
    create_error_alert,
    create_critical_alert
)

# Fixture for QApplication instance


@pytest.fixture(scope="session")
def app_instance():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestAlertObjectPool:
    def test_get_new_alert(self):
        pool = AlertObjectPool(max_size=2)
        alert1 = pool.get_alert(EnhancedFluentAlert)
        assert isinstance(alert1, EnhancedFluentAlert)
        assert len(pool._pool) == 0
        assert len(pool._active_alerts) == 1

    def test_return_and_reuse_alert(self, qtbot):
        pool = AlertObjectPool(max_size=2)
        alert1 = pool.get_alert(EnhancedFluentAlert)
        qtbot.addWidget(alert1)

        pool.return_alert(alert1)
        assert len(pool._pool) == 1
        assert len(pool._active_alerts) == 0

        alert2 = pool.get_alert(EnhancedFluentAlert)
        assert alert1 is alert2
        assert len(pool._pool) == 0
        assert len(pool._active_alerts) == 1

    def test_pool_max_size(self, qtbot):
        pool = AlertObjectPool(max_size=1)
        alert1 = pool.get_alert(EnhancedFluentAlert)
        alert2 = pool.get_alert(EnhancedFluentAlert)
        qtbot.addWidget(alert1)
        qtbot.addWidget(alert2)

        pool.return_alert(alert1)
        assert len(pool._pool) == 1

        pool.return_alert(alert2)
        # alert2 should be deleted, not added to the pool
        assert len(pool._pool) == 1
        assert pool._pool[0] is alert1


class TestAlertManager:
    @pytest.fixture(autouse=True)
    def reset_manager(self):
        # Reset the global manager before each test in this class
        alert_manager._active_alerts.clear()
        alert_manager._notification_queue.clear()
        alert_manager._pool = AlertObjectPool()
        yield

    def test_show_alert(self, qtbot):
        alert = EnhancedFluentAlert("Title", "Message")
        qtbot.addWidget(alert)
        # The alert registers itself with the manager on creation
        assert len(alert_manager._active_alerts) == 1
        assert alert_manager._active_alerts[0] is alert

    def test_max_concurrent_alerts(self, qtbot):
        alert_manager._max_concurrent = 2
        alerts = []
        for i in range(3):
            alert = EnhancedFluentAlert(f"Title {i}", f"Message {i}")
            qtbot.addWidget(alert)
            alerts.append(alert)

        assert len(alert_manager._active_alerts) == 2
        assert len(alert_manager._notification_queue) == 1
        assert alert_manager._active_alerts[0] is alerts[0]
        assert alert_manager._active_alerts[1] is alerts[1]
        assert alert_manager._notification_queue[0]['alert'] is alerts[2]

    def test_show_queued_alert_on_close(self, qtbot):
        alert_manager._max_concurrent = 1
        alert1 = EnhancedFluentAlert("Title 1", "Message 1")
        alert2 = EnhancedFluentAlert("Title 2", "Message 2")
        qtbot.addWidget(alert1)
        qtbot.addWidget(alert2)

        assert len(alert_manager._active_alerts) == 1
        assert len(alert_manager._notification_queue) == 1

        # Close the first alert
        alert1.close()
        qtbot.waitUntil(lambda: len(
            alert_manager._active_alerts) == 1, timeout=1000)
        qtbot.waitUntil(lambda: len(
            alert_manager._notification_queue) == 0, timeout=1000)

        assert alert_manager._active_alerts[0] is alert2


class TestEnhancedFluentAlert:
    def test_initialization(self, qtbot):
        alert = EnhancedFluentAlert(
            title="Test Title",
            message="Test Message",
            alert_type=AlertType.SUCCESS,
            closable=True,
            action_text="OK"
        )
        qtbot.addWidget(alert)

        assert alert._title == "Test Title"
        assert alert._message == "Test Message"
        assert alert._alert_type == AlertType.SUCCESS
        assert alert._closable
        assert alert._action_text == "OK"
        assert hasattr(alert, '_close_button')
        assert hasattr(alert, '_action_button')

    def test_close_signal(self, qtbot):
        alert = EnhancedFluentAlert(closable=True)
        qtbot.addWidget(alert)

        with qtbot.waitSignal(alert.closed, timeout=1000):
            alert.close_with_animation()

    def test_action_signal(self, qtbot):
        alert = EnhancedFluentAlert(action_text="Click Me")
        qtbot.addWidget(alert)

        with qtbot.waitSignal(alert.action_clicked, timeout=500):
            QTest.mouseClick(alert._action_button, Qt.MouseButton.LeftButton)

    def test_factory_functions(self, qtbot):
        info_alert = create_info_alert("Info", "Info message")
        qtbot.addWidget(info_alert)
        assert info_alert._alert_type == AlertType.INFO

        success_alert = create_success_alert("Success", "Success message")
        qtbot.addWidget(success_alert)
        assert success_alert._alert_type == AlertType.SUCCESS

        warning_alert = create_warning_alert("Warning", "Warning message")
        qtbot.addWidget(warning_alert)
        assert warning_alert._alert_type == AlertType.WARNING

        error_alert = create_error_alert("Error", "Error message")
        qtbot.addWidget(error_alert)
        assert error_alert._alert_type == AlertType.ERROR

        critical_alert = create_critical_alert("Critical", "Critical message")
        qtbot.addWidget(critical_alert)
        assert critical_alert._alert_type == AlertType.CRITICAL
        assert critical_alert._priority == AlertPriority.URGENT


class TestEnhancedFluentNotification:
    def test_initialization(self, qtbot):
        notification = EnhancedFluentNotification(
            title="Notify Title",
            message="Notify Message",
            notification_type=AlertType.WARNING,
            clickable=True
        )
        qtbot.addWidget(notification)

        assert notification._title == "Notify Title"
        assert notification._notification_type == AlertType.WARNING
        assert notification._clickable

    def test_clicked_signal(self, qtbot):
        notification = EnhancedFluentNotification(clickable=True)
        qtbot.addWidget(notification)
        notification.show()

        with qtbot.waitSignal(notification.clicked, timeout=500):
            QTest.mouseClick(notification, Qt.MouseButton.LeftButton)


class TestFluentMessageBar:
    def test_initialization(self, qtbot):
        bar = FluentMessageBar(
            message="Bar Message",
            message_type=AlertType.ERROR,
            action_text="Retry"
        )
        qtbot.addWidget(bar)

        assert bar._message == "Bar Message"
        assert bar._message_type == AlertType.ERROR
        assert hasattr(bar, '_action_button')

    def test_action_signal_message_bar(self, qtbot):
        bar = FluentMessageBar(action_text="Action")
        qtbot.addWidget(bar)

        with qtbot.waitSignal(bar.action_clicked, timeout=500):
            QTest.mouseClick(bar._action_button, Qt.MouseButton.LeftButton)

    def test_close_signal_message_bar(self, qtbot):
        bar = FluentMessageBar(closable=True)
        qtbot.addWidget(bar)

        with qtbot.waitSignal(bar.closed, timeout=1000):
            bar._close_clicked()
