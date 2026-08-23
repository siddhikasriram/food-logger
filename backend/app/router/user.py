from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.shared.exceptions import NotFoundError
from app.schema.user import UserCreate, UserRead, UserUpdate
from app.controller.user import UserController

router = APIRouter(prefix="/users", tags=["users"])


def get_user_controller(db: Session = Depends(db_session)) -> UserController:
    return UserController(db)


@router.get("", response_model=list[UserRead])
def list_users(controller: UserController = Depends(get_user_controller)) -> list[UserRead]:
    return controller.list_users()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate, controller: UserController = Depends(get_user_controller)
) -> UserRead:
    return controller.create_user(payload)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, controller: UserController = Depends(get_user_controller)) -> UserRead:
    user = controller.get_user(user_id)
    if user is None:
        raise NotFoundError("User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    controller: UserController = Depends(get_user_controller),
) -> UserRead:
    return controller.update_user(user_id, payload)
