from datetime import date

from sqlalchemy.orm import Session

from app.nutrition.schemas import DailyProteinSummary, NutritionTotals


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

    def recommended_protein_g(self, weight_kg: float, protein_factor: float = 1.4) -> float:
        raise NotImplementedError("Protein target calculation is not implemented in this scaffold.")

    def ingredient_nutrition(self, ingredient_id: int, quantity_g: float) -> NutritionTotals:
        raise NotImplementedError("Ingredient nutrition is not implemented in this scaffold.")

    def recipe_nutrition(self, recipe_id: int) -> NutritionTotals:
        raise NotImplementedError("Recipe nutrition is not implemented in this scaffold.")

    def meal_nutrition(self, recipe_id: int, servings: float) -> NutritionTotals:
        raise NotImplementedError("Meal nutrition is not implemented in this scaffold.")

    def daily_protein(self, user_id: int, day: date) -> DailyProteinSummary:
        raise NotImplementedError("Daily protein summary is not implemented in this scaffold.")
