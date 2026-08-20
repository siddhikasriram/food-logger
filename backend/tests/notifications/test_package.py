def test_notification_service_stub() -> None:
    from app.notifications.service import NotificationService

    assert hasattr(NotificationService, "list_for_user")
