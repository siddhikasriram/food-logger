from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.nutrition.schemas import DailyProteinSummary
from app.nutrition.service import NutritionService

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


def get_nutrition_service(db: Session = Depends(db_session)) -> NutritionService:
    return NutritionService(db)


@router.get("/users/{user_id}/daily", response_model=DailyProteinSummary)
def get_daily_protein(
    user_id: int,
    day: date | None = Query(default=None),
    service: NutritionService = Depends(get_nutrition_service),
) -> DailyProteinSummary:
    return service.daily_protein(user_id, day or date.today())
