from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: Session = Depends(db_session)) -> UserService:
    return UserService(db)


@router.get("/{user_id}")
def get_user(user_id: int, service: UserService = Depends(get_user_service)) -> dict:
    """Fetch a user profile. Implementation deferred."""
    _ = (user_id, service)
    raise NotImplementedError("User endpoints are not implemented in this scaffold.")
