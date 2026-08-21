from datetime import date

from sqlalchemy.orm import Session

from app.ingredients.models import Ingredient
from app.meals.repository import MealLogRepository
from app.nutrition.schemas import DailyProteinSummary, NutritionTotals
from app.recipes.models import Recipe
from app.shared.exceptions import NotFoundError
from app.users.models import User


class NutritionService:
    """Reusable nutrition math. Do not call this from routes except via this service.

    Ingredient nutrition is always per 100g:
        value = per_100g * (quantity_g / 100)
    Recipe nutrition is the sum of ingredient quantities.
    Meal nutrition is recipe nutrition × servings.
    Daily totals come from meal_logs, not a stored aggregate.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.meal_logs = MealLogRepository(db)

    def recommended_protein_g(self, weight_kg: float, protein_factor: float = 1.4) -> float:
        return weight_kg * protein_factor

    def ingredient_nutrition(self, ingredient_id: int, quantity_g: float) -> NutritionTotals:
        ingredient = self.db.get(Ingredient, ingredient_id)
        if ingredient is None:
            raise NotFoundError("Ingredient not found")
        factor = quantity_g / 100.0
        return NutritionTotals(
            calories=float(ingredient.calories_per_100g) * factor,
            protein_g=float(ingredient.protein_per_100g) * factor,
            carbs_g=float(ingredient.carbs_per_100g) * factor,
            fat_g=float(ingredient.fat_per_100g) * factor,
            fiber_g=float(ingredient.fiber_per_100g) * factor,
        )

    def recipe_nutrition(self, recipe_id: int) -> NutritionTotals:
        recipe = self.db.get(Recipe, recipe_id)
        if recipe is None:
            raise NotFoundError("Recipe not found")
        totals = NutritionTotals()
        for row in recipe.recipe_ingredients:
            part = self.ingredient_nutrition(row.ingredient_id, float(row.quantity_g))
            totals = NutritionTotals(
                calories=totals.calories + part.calories,
                protein_g=totals.protein_g + part.protein_g,
                carbs_g=totals.carbs_g + part.carbs_g,
                fat_g=totals.fat_g + part.fat_g,
                fiber_g=totals.fiber_g + part.fiber_g,
            )
        return totals

    def meal_nutrition(self, recipe_id: int, servings: float) -> NutritionTotals:
        recipe = self.recipe_nutrition(recipe_id)
        return NutritionTotals(
            calories=recipe.calories * servings,
            protein_g=recipe.protein_g * servings,
            carbs_g=recipe.carbs_g * servings,
            fat_g=recipe.fat_g * servings,
            fiber_g=recipe.fiber_g * servings,
        )

    def daily_protein(self, user_id: int, day: date) -> DailyProteinSummary:
        user = self.db.get(User, user_id)
        if user is None:
            raise NotFoundError("User not found")

        consumed = 0.0
        for meal_log in self.meal_logs.list_for_user_on_date(user_id, day):
            meal = self.meal_nutrition(meal_log.recipe_id, float(meal_log.servings))
            consumed += meal.protein_g

        goal = float(user.protein_goal_g) if user.protein_goal_g is not None else 0.0
        remaining = max(0.0, goal - consumed)
        progress = (consumed / goal * 100.0) if goal > 0 else 0.0
        return DailyProteinSummary(
            protein_goal_g=goal,
            protein_consumed_g=consumed,
            protein_remaining_g=remaining,
            progress_percent=progress,
        )
