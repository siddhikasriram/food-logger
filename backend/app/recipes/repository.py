from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.recipes.models import Recipe, RecipeIngredient, RecipeTag, RecipeTagMapping


class RecipeRepository:
    """Data access for global recipes, ingredients, and tags."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _eager(self):
        return self.db.query(Recipe).options(
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.tag_mappings).selectinload(RecipeTagMapping.tag),
        )

    def get_by_id(self, recipe_id: int) -> Recipe | None:
        return self._eager().filter(Recipe.recipe_id == recipe_id).one_or_none()

    def list_all(self) -> list[Recipe]:
        return self._eager().order_by(Recipe.name).all()

    def get_by_name(self, name: str) -> Recipe | None:
        return (
            self._eager()
            .filter(func.lower(Recipe.name) == name.strip().lower())
            .one_or_none()
        )

    def get_tag_by_id(self, tag_id: int) -> RecipeTag | None:
        return self.db.get(RecipeTag, tag_id)

    def get_tag_by_name(self, name: str) -> RecipeTag | None:
        return self.db.query(RecipeTag).filter(RecipeTag.name == name).one_or_none()

    def add(self, recipe: Recipe) -> Recipe:
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        loaded = self.get_by_id(recipe.recipe_id)
        assert loaded is not None
        return loaded
