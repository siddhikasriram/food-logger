from datetime import datetime

from sqlalchemy.orm import Session

from app.chat.provider import MealParser
from app.chat.schemas import (
    ChatConfirmResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatProposal,
    ParsedIngredient,
)
from app.ingredients.models import Ingredient
from app.ingredients.repository import IngredientRepository
from app.meals.models import MealLog
from app.meals.schemas import MealLogRead
from app.nutrition.schemas import NutritionTotals
from app.nutrition.service import NutritionService
from app.recipes.models import Recipe, RecipeIngredient
from app.recipes.repository import RecipeRepository
from app.shared.enums import NutritionSource
from app.shared.exceptions import AppError, NotFoundError, ServiceUnavailableError
from app.users.repository import UserRepository


class ChatService:
    def __init__(self, db: Session, parser: MealParser) -> None:
        self.db = db
        self.parser = parser
        self.users = UserRepository(db)
        self.ingredients = IngredientRepository(db)
        self.recipes = RecipeRepository(db)

    def propose(self, payload: ChatMessageRequest) -> ChatMessageResponse:
        if self.users.get_by_id(payload.user_id) is None:
            raise NotFoundError("User not found")

        parsed = self.parser.parse(payload.message, self._catalog_context())
        recipe = self._match_recipe(parsed.recipe_id, parsed.recipe_name)
        if recipe is not None:
            ingredients = [self._existing_ingredient(row.ingredient, float(row.quantity_g)) for row in recipe.recipe_ingredients]
            recipe_id = recipe.recipe_id
            recipe_name = recipe.name
            description = recipe.description
        else:
            if not parsed.ingredients:
                raise ServiceUnavailableError(
                    "The meal assistant could not identify ingredients for that recipe."
                )
            ingredients = self._resolve_proposed_ingredients(parsed.ingredients)
            recipe_id = None
            recipe_name = parsed.recipe_name.strip()
            description = parsed.description

        ingredients = self._merge_ingredients(ingredients)
        contains_estimates = any(item.is_estimate for item in ingredients)
        proposal = ChatProposal(
            user_id=payload.user_id,
            recipe_id=recipe_id,
            recipe_name=recipe_name,
            description=description,
            servings=parsed.servings,
            meal_type=parsed.meal_type,
            consumed_at=payload.consumed_at or datetime.now(),
            ingredients=ingredients,
            contains_estimates=contains_estimates,
        )
        macros = self._proposal_macros(proposal)
        qualifier = " Estimated nutrition is included." if contains_estimates else ""
        return ChatMessageResponse(
            assistant_message=(
                f"I found {proposal.recipe_name} with {proposal.servings:g} "
                f"serving(s).{qualifier} Confirm to save it to today's log."
            ),
            proposal=proposal,
            meal_macros=macros,
        )

    def confirm(self, proposal: ChatProposal) -> ChatConfirmResponse:
        if self.users.get_by_id(proposal.user_id) is None:
            raise NotFoundError("User not found")

        created_recipe = False
        try:
            recipe = self._match_recipe(proposal.recipe_id, proposal.recipe_name)
            if recipe is None:
                if not proposal.ingredients:
                    raise AppError("A new recipe must include at least one ingredient.")
                recipe_ingredients: list[RecipeIngredient] = []
                for item in self._merge_ingredients(proposal.ingredients):
                    ingredient = self._materialize_ingredient(item)
                    recipe_ingredients.append(
                        RecipeIngredient(
                            ingredient_id=ingredient.ingredient_id,
                            quantity_g=item.quantity_g,
                        )
                    )
                recipe = Recipe(
                    name=proposal.recipe_name.strip(),
                    description=proposal.description,
                    servings=1,
                    created_by=proposal.user_id,
                    recipe_ingredients=recipe_ingredients,
                )
                self.db.add(recipe)
                self.db.flush()
                created_recipe = True

            meal_log = MealLog(
                user_id=proposal.user_id,
                recipe_id=recipe.recipe_id,
                meal_type=proposal.meal_type,
                servings=proposal.servings,
                consumed_at=proposal.consumed_at,
            )
            self.db.add(meal_log)
            self.db.flush()

            nutrition = NutritionService(self.db)
            meal_macros = nutrition.meal_nutrition(recipe.recipe_id, proposal.servings)
            daily = nutrition.daily_protein(
                proposal.user_id, proposal.consumed_at.date()
            )
            contains_estimates = any(
                self.db.get(Ingredient, row.ingredient_id).nutrition_source
                == NutritionSource.LLM_ESTIMATE
                for row in recipe.recipe_ingredients
            )
            self.db.commit()
            self.db.refresh(meal_log)
        except Exception:
            self.db.rollback()
            raise

        meal_read = MealLogRead(
            meal_log_id=meal_log.meal_log_id,
            user_id=meal_log.user_id,
            recipe_id=recipe.recipe_id,
            recipe_name=recipe.name,
            meal_type=meal_log.meal_type,
            servings=float(meal_log.servings),
            consumed_at=meal_log.consumed_at,
            created_at=meal_log.created_at,
        )
        return ChatConfirmResponse(
            assistant_message=(
                f"Logged {recipe.name}: {meal_macros.protein_g:.1f}g protein. "
                f"You have {daily.protein_remaining_g:.1f}g remaining today."
            ),
            meal_log=meal_read,
            meal_macros=meal_macros,
            daily_protein=daily,
            created_recipe=created_recipe,
            contains_estimates=contains_estimates,
        )

    def _catalog_context(self) -> dict[str, object]:
        ingredients = [
            {
                "id": item.ingredient_id,
                "name": item.name,
                "calories_per_100g": float(item.calories_per_100g),
                "protein_per_100g": float(item.protein_per_100g),
                "carbs_per_100g": float(item.carbs_per_100g),
                "fat_per_100g": float(item.fat_per_100g),
                "fiber_per_100g": float(item.fiber_per_100g),
            }
            for item in self.ingredients.list_all()
        ]
        recipes = [
            {
                "id": recipe.recipe_id,
                "name": recipe.name,
                "ingredients": [
                    {
                        "ingredient_id": row.ingredient_id,
                        "name": row.ingredient.name,
                        "quantity_g": float(row.quantity_g),
                    }
                    for row in recipe.recipe_ingredients
                ],
            }
            for recipe in self.recipes.list_all()
        ]
        return {"recipes": recipes, "ingredients": ingredients}

    def _match_recipe(self, recipe_id: int | None, name: str) -> Recipe | None:
        if recipe_id is not None:
            recipe = self.recipes.get_by_id(recipe_id)
            if recipe is None:
                raise ServiceUnavailableError(
                    "The selected catalog recipe is no longer available."
                )
            return recipe
        return self.recipes.get_by_name(name)

    def _resolve_proposed_ingredients(
        self, parsed: list[ParsedIngredient]
    ) -> list[ParsedIngredient]:
        resolved: list[ParsedIngredient] = []
        for item in parsed:
            ingredient = None
            if item.ingredient_id is not None:
                ingredient = self.ingredients.get_by_id(item.ingredient_id)
                if ingredient is None:
                    raise ServiceUnavailableError(
                        "A selected catalog ingredient is no longer available."
                    )
            else:
                ingredient = self.ingredients.get_by_name(item.name)
            resolved.append(
                self._existing_ingredient(ingredient, item.quantity_g)
                if ingredient is not None
                else item
            )
        return resolved

    def _existing_ingredient(
        self, ingredient: Ingredient, quantity_g: float
    ) -> ParsedIngredient:
        return ParsedIngredient(
            ingredient_id=ingredient.ingredient_id,
            name=ingredient.name,
            quantity_g=quantity_g,
            calories_per_100g=float(ingredient.calories_per_100g),
            protein_per_100g=float(ingredient.protein_per_100g),
            carbs_per_100g=float(ingredient.carbs_per_100g),
            fat_per_100g=float(ingredient.fat_per_100g),
            fiber_per_100g=float(ingredient.fiber_per_100g),
            is_estimate=ingredient.nutrition_source == NutritionSource.LLM_ESTIMATE,
        )

    def _merge_ingredients(
        self, ingredients: list[ParsedIngredient]
    ) -> list[ParsedIngredient]:
        merged: dict[str, ParsedIngredient] = {}
        for item in ingredients:
            key = (
                f"id:{item.ingredient_id}"
                if item.ingredient_id is not None
                else f"name:{item.name.strip().lower()}"
            )
            if key in merged:
                current = merged[key]
                merged[key] = current.model_copy(
                    update={"quantity_g": current.quantity_g + item.quantity_g}
                )
            else:
                merged[key] = item
        return list(merged.values())

    def _materialize_ingredient(self, item: ParsedIngredient) -> Ingredient:
        if item.ingredient_id is not None:
            ingredient = self.ingredients.get_by_id(item.ingredient_id)
            if ingredient is None:
                raise ServiceUnavailableError(
                    "A selected catalog ingredient is no longer available."
                )
        else:
            ingredient = self.ingredients.get_by_name(item.name)
        if ingredient is not None:
            return ingredient

        ingredient = Ingredient(
            name=item.name.strip(),
            calories_per_100g=item.calories_per_100g,
            protein_per_100g=item.protein_per_100g,
            carbs_per_100g=item.carbs_per_100g,
            fat_per_100g=item.fat_per_100g,
            fiber_per_100g=item.fiber_per_100g,
            nutrition_source=NutritionSource.LLM_ESTIMATE,
        )
        self.db.add(ingredient)
        self.db.flush()
        return ingredient

    def _proposal_macros(self, proposal: ChatProposal) -> NutritionTotals:
        if proposal.recipe_id is not None:
            return NutritionService(self.db).meal_nutrition(
                proposal.recipe_id, proposal.servings
            )

        totals = NutritionTotals()
        for item in proposal.ingredients:
            factor = item.quantity_g / 100
            totals = NutritionTotals(
                calories=totals.calories + float(item.calories_per_100g or 0) * factor,
                protein_g=totals.protein_g + float(item.protein_per_100g or 0) * factor,
                carbs_g=totals.carbs_g + float(item.carbs_per_100g or 0) * factor,
                fat_g=totals.fat_g + float(item.fat_per_100g or 0) * factor,
                fiber_g=totals.fiber_g + float(item.fiber_per_100g or 0) * factor,
            )
        return NutritionTotals(
            calories=totals.calories * proposal.servings,
            protein_g=totals.protein_g * proposal.servings,
            carbs_g=totals.carbs_g * proposal.servings,
            fat_g=totals.fat_g * proposal.servings,
            fiber_g=totals.fiber_g * proposal.servings,
        )
