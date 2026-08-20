from sqlalchemy.orm import Session

from app.ingredients.models import Ingredient


class IngredientRepository:
    """Data access for the global ingredient catalog."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, ingredient_id: int) -> Ingredient | None:
        return self.db.get(Ingredient, ingredient_id)

    def get_by_name(self, name: str) -> Ingredient | None:
        return self.db.query(Ingredient).filter(Ingredient.name == name).one_or_none()
