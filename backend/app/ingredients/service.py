from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.ingredients.models import Ingredient
from app.ingredients.repository import IngredientRepository
from app.ingredients.schemas import IngredientCreate, IngredientRead
from app.shared.exceptions import ConflictError


class IngredientService:
    """Global ingredient catalog. Nutrition math lives in the nutrition domain."""

    def __init__(self, db: Session) -> None:
        self.repository = IngredientRepository(db)

    def get_ingredient(self, ingredient_id: int) -> IngredientRead | None:
        ingredient = self.repository.get_by_id(ingredient_id)
        if ingredient is None:
            return None
        return IngredientRead.model_validate(ingredient)

    def list_ingredients(self) -> list[IngredientRead]:
        return [
            IngredientRead.model_validate(ingredient)
            for ingredient in self.repository.list_all()
        ]

    def create_ingredient(self, payload: IngredientCreate) -> IngredientRead:
        if self.repository.get_by_name(payload.name) is not None:
            raise ConflictError("An ingredient with this name already exists.")

        ingredient = Ingredient(
            name=payload.name,
            calories_per_100g=payload.calories_per_100g,
            protein_per_100g=payload.protein_per_100g,
            carbs_per_100g=payload.carbs_per_100g,
            fat_per_100g=payload.fat_per_100g,
            fiber_per_100g=payload.fiber_per_100g,
        )
        try:
            ingredient = self.repository.add(ingredient)
        except IntegrityError as exc:
            self.repository.db.rollback()
            raise ConflictError("An ingredient with this name already exists.") from exc
        return IngredientRead.model_validate(ingredient)
