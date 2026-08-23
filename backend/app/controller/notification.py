from app.schema.notification import NotificationRead


class NotificationController:
    """Placeholder for future notification delivery. No persistence in this scaffold."""

    def list_for_user(self, user_id: int) -> list[NotificationRead]:
        raise NotImplementedError("Notifications are not implemented in this scaffold.")
