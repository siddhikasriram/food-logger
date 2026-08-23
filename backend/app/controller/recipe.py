from sqlalchemy.orm import Session

from app.repository.ingredient import IngredientRepository
from app.model.recipe import Recipe, RecipeIngredient, RecipeTagMapping
from app.repository.recipe import RecipeRepository
from app.schema.recipe import (
    RecipeCreate,
    RecipeIngredientDetail,
    RecipeRead,
    RecipeTagRead,
)
from app.shared.exceptions import NotFoundError
from app.repository.user import UserRepository


class RecipeController:
    """Global recipe catalog. Nutrition is derived via the nutrition domain, not stored here."""

    def __init__(self, db: Session) -> None:
        self.repository = RecipeRepository(db)
        self.ingredients = IngredientRepository(db)
        self.users = UserRepository(db)

    def get_recipe(self, recipe_id: int) -> RecipeRead | None:
        recipe = self.repository.get_by_id(recipe_id)
        if recipe is None:
            return None
        return self._to_read(recipe)

    def list_recipes(self) -> list[RecipeRead]:
        return [self._to_read(recipe) for recipe in self.repository.list_all()]

    def create_recipe(self, payload: RecipeCreate) -> RecipeRead:
        if payload.created_by is not None and self.users.get_by_id(payload.created_by) is None:
            raise NotFoundError("User not found")

        for item in payload.ingredients:
            if self.ingredients.get_by_id(item.ingredient_id) is None:
                raise NotFoundError(f"Ingredient {item.ingredient_id} not found")

        for tag_id in payload.tag_ids:
            if self.repository.get_tag_by_id(tag_id) is None:
                raise NotFoundError(f"Tag {tag_id} not found")

        recipe = Recipe(
            name=payload.name,
            description=payload.description,
            instructions=payload.instructions,
            servings=payload.servings,
            created_by=payload.created_by,
            recipe_ingredients=[
                RecipeIngredient(
                    ingredient_id=item.ingredient_id,
                    quantity_g=item.quantity_g,
                )
                for item in payload.ingredients
            ],
            tag_mappings=[
                RecipeTagMapping(tag_id=tag_id) for tag_id in payload.tag_ids
            ],
        )
        recipe = self.repository.add(recipe)
        return self._to_read(recipe)

    def _to_read(self, recipe: Recipe) -> RecipeRead:
        return RecipeRead(
            recipe_id=recipe.recipe_id,
            name=recipe.name,
            description=recipe.description,
            instructions=recipe.instructions,
            servings=float(recipe.servings),
            created_by=recipe.created_by,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
            ingredients=[
                RecipeIngredientDetail(
                    ingredient_id=row.ingredient_id,
                    name=row.ingredient.name,
                    quantity_g=float(row.quantity_g),
                )
                for row in recipe.recipe_ingredients
            ],
            tags=[
                RecipeTagRead(tag_id=mapping.tag.tag_id, name=mapping.tag.name)
                for mapping in recipe.tag_mappings
            ],
        )
