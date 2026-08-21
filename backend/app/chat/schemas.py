from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.meals.schemas import MealLogRead
from app.nutrition.schemas import DailyProteinSummary, NutritionTotals
from app.shared.enums import MealType


class ParsedIngredient(BaseModel):
    ingredient_id: int | None
    name: str = Field(min_length=1, max_length=255)
    quantity_g: float = Field(gt=0)
    calories_per_100g: float | None
    protein_per_100g: float | None
    carbs_per_100g: float | None
    fat_per_100g: float | None
    fiber_per_100g: float | None
    is_estimate: bool = False

    @model_validator(mode="after")
    def require_estimated_macros(self) -> "ParsedIngredient":
        if self.ingredient_id is None:
            values = (
                self.calories_per_100g,
                self.protein_per_100g,
                self.carbs_per_100g,
                self.fat_per_100g,
                self.fiber_per_100g,
            )
            if any(value is None or value < 0 for value in values):
                raise ValueError("New ingredients require non-negative macro estimates")
            self.is_estimate = True
        return self


class ParsedMeal(BaseModel):
    recipe_id: int | None
    recipe_name: str = Field(min_length=1, max_length=255)
    description: str | None
    servings: float = Field(gt=0)
    meal_type: MealType
    ingredients: list[ParsedIngredient]


class ChatMessageRequest(BaseModel):
    user_id: int
    message: str = Field(min_length=1, max_length=2000)
    consumed_at: datetime | None = None


class ChatProposal(BaseModel):
    user_id: int
    recipe_id: int | None
    recipe_name: str
    description: str | None
    servings: float = Field(gt=0)
    meal_type: MealType
    consumed_at: datetime
    ingredients: list[ParsedIngredient]
    contains_estimates: bool


class ChatMessageResponse(BaseModel):
    assistant_message: str
    needs_confirmation: bool = True
    proposal: ChatProposal
    meal_macros: NutritionTotals


class ChatConfirmRequest(BaseModel):
    proposal: ChatProposal


class ChatConfirmResponse(BaseModel):
    assistant_message: str
    meal_log: MealLogRead
    meal_macros: NutritionTotals
    daily_protein: DailyProteinSummary
    created_recipe: bool
    contains_estimates: bool
