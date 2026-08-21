from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ingredients.models import Ingredient


class IngredientRepository:
    """Data access for the global ingredient catalog."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, ingredient_id: int) -> Ingredient | None:
        return self.db.get(Ingredient, ingredient_id)

    def get_by_name(self, name: str) -> Ingredient | None:
        return (
            self.db.query(Ingredient)
            .filter(func.lower(Ingredient.name) == name.strip().lower())
            .one_or_none()
        )

    def list_all(self) -> list[Ingredient]:
        return self.db.query(Ingredient).order_by(Ingredient.name).all()

    def add(self, ingredient: Ingredient) -> Ingredient:
        self.db.add(ingredient)
        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient
