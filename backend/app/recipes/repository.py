from sqlalchemy.orm import Session

from app.recipes.models import Recipe, RecipeTag


class RecipeRepository:
    """Data access for global recipes, ingredients, and tags."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, recipe_id: int) -> Recipe | None:
        return self.db.get(Recipe, recipe_id)

    def get_tag_by_name(self, name: str) -> RecipeTag | None:
        return self.db.query(RecipeTag).filter(RecipeTag.name == name).one_or_none()
