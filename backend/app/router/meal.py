from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.schema.meal import MealLogCreate, MealLogRead
from app.controller.meal import MealController
from app.shared.exceptions import NotFoundError

router = APIRouter(prefix="/meals", tags=["meals"])


def get_meal_controller(db: Session = Depends(db_session)) -> MealController:
    return MealController(db)


@router.get("", response_model=list[MealLogRead])
def list_meals(
    user_id: int,
    day: date,
    controller: MealController = Depends(get_meal_controller),
) -> list[MealLogRead]:
    return controller.list_for_user_on_date(user_id, day)


@router.post("", response_model=MealLogRead, status_code=status.HTTP_201_CREATED)
def create_meal(
    payload: MealLogCreate, controller: MealController = Depends(get_meal_controller)
) -> MealLogRead:
    return controller.log_meal(payload)


@router.get("/{meal_log_id}", response_model=MealLogRead)
def get_meal_log(
    meal_log_id: int, controller: MealController = Depends(get_meal_controller)
) -> MealLogRead:
    meal_log = controller.get_meal_log(meal_log_id)
    if meal_log is None:
        raise NotFoundError("Meal log not found")
    return meal_log


@router.delete("/{meal_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_log(
    meal_log_id: int, controller: MealController = Depends(get_meal_controller)
) -> None:
    controller.delete_meal_log(meal_log_id)
