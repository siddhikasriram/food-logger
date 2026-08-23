from datetime import date

from sqlalchemy.orm import Session

from app.model.meal import MealLog
from app.repository.meal import MealLogRepository
from app.schema.meal import MealLogCreate, MealLogRead
from app.repository.recipe import RecipeRepository
from app.shared.exceptions import NotFoundError
from app.repository.user import UserRepository


class MealController:
    """Meal logging. Consumed nutrition = recipe nutrition × servings (nutrition domain)."""

    def __init__(self, db: Session) -> None:
        self.repository = MealLogRepository(db)
        self.users = UserRepository(db)
        self.recipes = RecipeRepository(db)

    def get_meal_log(self, meal_log_id: int) -> MealLogRead | None:
        meal_log = self.repository.get_by_id(meal_log_id)
        if meal_log is None:
            return None
        return self._to_read(meal_log)

    def list_for_user_on_date(self, user_id: int, day: date) -> list[MealLogRead]:
        if self.users.get_by_id(user_id) is None:
            raise NotFoundError("User not found")
        return [
            self._to_read(meal_log)
            for meal_log in self.repository.list_for_user_on_date(user_id, day)
        ]

    def log_meal(self, payload: MealLogCreate) -> MealLogRead:
        if self.users.get_by_id(payload.user_id) is None:
            raise NotFoundError("User not found")
        if self.recipes.get_by_id(payload.recipe_id) is None:
            raise NotFoundError("Recipe not found")

        meal_log = MealLog(
            user_id=payload.user_id,
            recipe_id=payload.recipe_id,
            meal_type=payload.meal_type,
            servings=payload.servings,
            consumed_at=payload.consumed_at,
        )
        meal_log = self.repository.add(meal_log)
        return self._to_read(meal_log)

    def delete_meal_log(self, meal_log_id: int) -> None:
        meal_log = self.repository.get_by_id(meal_log_id)
        if meal_log is None:
            raise NotFoundError("Meal log not found")
        self.repository.delete(meal_log)

    def _to_read(self, meal_log: MealLog) -> MealLogRead:
        return MealLogRead(
            meal_log_id=meal_log.meal_log_id,
            user_id=meal_log.user_id,
            recipe_id=meal_log.recipe_id,
            recipe_name=meal_log.recipe.name,
            meal_type=meal_log.meal_type,
            servings=float(meal_log.servings),
            consumed_at=meal_log.consumed_at,
            created_at=meal_log.created_at,
        )
