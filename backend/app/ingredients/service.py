from sqlalchemy.orm import Session

from app.ingredients.repository import IngredientRepository
from app.ingredients.schemas import IngredientCreate, IngredientRead


class IngredientService:
    """Global ingredient catalog. Nutrition math lives in the nutrition domain."""

    def __init__(self, db: Session) -> None:
        self.repository = IngredientRepository(db)

    def get_ingredient(self, ingredient_id: int) -> IngredientRead | None:
        ingredient = self.repository.get_by_id(ingredient_id)
        if ingredient is None:
            return None
        return IngredientRead.model_validate(ingredient)

    def create_ingredient(self, payload: IngredientCreate) -> IngredientRead:
        raise NotImplementedError("Ingredient creation is not implemented in this scaffold.")
