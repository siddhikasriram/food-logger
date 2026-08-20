from fastapi import APIRouter, Depends

from app.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_notification_service() -> NotificationService:
    return NotificationService()


@router.get("/")
def list_notifications(
    service: NotificationService = Depends(get_notification_service),
) -> list:
    """List notifications. Implementation deferred."""
    _ = service
    raise NotImplementedError("Notification endpoints are not implemented in this scaffold.")
