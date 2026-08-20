from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.meals.service import MealService

router = APIRouter(prefix="/meals", tags=["meals"])


def get_meal_service(db: Session = Depends(db_session)) -> MealService:
    return MealService(db)


@router.get("/{meal_log_id}")
def get_meal_log(meal_log_id: int, service: MealService = Depends(get_meal_service)) -> dict:
    """Fetch a meal log. Implementation deferred."""
    _ = (meal_log_id, service)
    raise NotImplementedError("Meal log endpoints are not implemented in this scaffold.")
