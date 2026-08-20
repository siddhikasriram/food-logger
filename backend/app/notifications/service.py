from app.notifications.schemas import NotificationRead


class NotificationService:
    """Placeholder for future notification delivery. No persistence in this scaffold."""

    def list_for_user(self, user_id: int) -> list[NotificationRead]:
        raise NotImplementedError("Notifications are not implemented in this scaffold.")
