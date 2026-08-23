def test_notification_controller_stub() -> None:
    from app.controller.notification import NotificationController

    assert hasattr(NotificationController, "list_for_user")
