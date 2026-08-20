from pydantic import BaseModel


class NotificationRead(BaseModel):
    notification_id: int
    user_id: int
    message: str
    read: bool = False
