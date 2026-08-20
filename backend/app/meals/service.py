from sqlalchemy.orm import Session

from app.meals.repository import MealLogRepository
from app.meals.schemas import MealLogCreate, MealLogRead


class MealService:
    """Meal logging. Consumed nutrition = recipe nutrition × servings (nutrition domain)."""

    def __init__(self, db: Session) -> None:
        self.repository = MealLogRepository(db)

    def get_meal_log(self, meal_log_id: int) -> MealLogRead | None:
        meal_log = self.repository.get_by_id(meal_log_id)
        if meal_log is None:
            return None
        return MealLogRead.model_validate(meal_log)

    def log_meal(self, payload: MealLogCreate) -> MealLogRead:
        raise NotImplementedError("Meal logging is not implemented in this scaffold.")
