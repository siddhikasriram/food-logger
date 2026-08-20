from sqlalchemy.orm import Session

from app.recipes.repository import RecipeRepository
from app.recipes.schemas import RecipeCreate, RecipeRead


class RecipeService:
    """Global recipe catalog. Nutrition is derived via the nutrition domain, not stored here."""

    def __init__(self, db: Session) -> None:
        self.repository = RecipeRepository(db)

    def get_recipe(self, recipe_id: int) -> RecipeRead | None:
        recipe = self.repository.get_by_id(recipe_id)
        if recipe is None:
            return None
        return RecipeRead.model_validate(recipe)

    def create_recipe(self, payload: RecipeCreate) -> RecipeRead:
        raise NotImplementedError("Recipe creation is not implemented in this scaffold.")
