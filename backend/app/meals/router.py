from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.meals.schemas import MealLogCreate, MealLogRead
from app.meals.service import MealService
from app.shared.exceptions import NotFoundError

router = APIRouter(prefix="/meals", tags=["meals"])


def get_meal_service(db: Session = Depends(db_session)) -> MealService:
    return MealService(db)


@router.get("", response_model=list[MealLogRead])
def list_meals(
    user_id: int,
    day: date,
    service: MealService = Depends(get_meal_service),
) -> list[MealLogRead]:
    return service.list_for_user_on_date(user_id, day)


@router.post("", response_model=MealLogRead, status_code=status.HTTP_201_CREATED)
def create_meal(
    payload: MealLogCreate, service: MealService = Depends(get_meal_service)
) -> MealLogRead:
    return service.log_meal(payload)


@router.get("/{meal_log_id}", response_model=MealLogRead)
def get_meal_log(
    meal_log_id: int, service: MealService = Depends(get_meal_service)
) -> MealLogRead:
    meal_log = service.get_meal_log(meal_log_id)
    if meal_log is None:
        raise NotFoundError("Meal log not found")
    return meal_log


@router.delete("/{meal_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_log(
    meal_log_id: int, service: MealService = Depends(get_meal_service)
) -> None:
    service.delete_meal_log(meal_log_id)
