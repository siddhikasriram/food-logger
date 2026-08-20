from datetime import date

from sqlalchemy.orm import Session

from app.meals.models import MealLog


class MealLogRepository:
    """Data access for meal logs. Daily totals are derived from these rows, not stored."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, meal_log_id: int) -> MealLog | None:
        return self.db.get(MealLog, meal_log_id)

    def list_for_user_on_date(self, user_id: int, day: date) -> list[MealLog]:
        raise NotImplementedError("Meal log queries are not implemented in this scaffold.")
