from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.shared.exceptions import NotFoundError
from app.users.schemas import UserCreate, UserRead, UserUpdate
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: Session = Depends(db_session)) -> UserService:
    return UserService(db)


@router.get("", response_model=list[UserRead])
def list_users(service: UserService = Depends(get_user_service)) -> list[UserRead]:
    return service.list_users()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate, service: UserService = Depends(get_user_service)
) -> UserRead:
    return service.create_user(payload)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, service: UserService = Depends(get_user_service)) -> UserRead:
    user = service.get_user(user_id)
    if user is None:
        raise NotFoundError("User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return service.update_user(user_id, payload)
