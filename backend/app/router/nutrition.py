from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.schema.nutrition import DailyProteinSummary
from app.controller.nutrition import NutritionController

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


def get_nutrition_controller(db: Session = Depends(db_session)) -> NutritionController:
    return NutritionController(db)


@router.get("/users/{user_id}/daily", response_model=DailyProteinSummary)
def get_daily_protein(
    user_id: int,
    day: date | None = Query(default=None),
    controller: NutritionController = Depends(get_nutrition_controller),
) -> DailyProteinSummary:
    return controller.daily_protein(user_id, day or date.today())
