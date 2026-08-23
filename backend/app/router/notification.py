from fastapi import APIRouter, Depends

from app.controller.notification import NotificationController

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_notification_controller() -> NotificationController:
    return NotificationController()


@router.get("/")
def list_notifications(
    controller: NotificationController = Depends(get_notification_controller),
) -> list:
    """List notifications. Implementation deferred."""
    _ = controller
    raise NotImplementedError("Notification endpoints are not implemented in this scaffold.")
