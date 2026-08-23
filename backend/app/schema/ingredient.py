from datetime import datetime

from pydantic import BaseModel, Field

from app.shared.enums import NutritionSource


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    calories_per_100g: float = Field(ge=0)
    protein_per_100g: float = Field(ge=0)
    carbs_per_100g: float = Field(ge=0)
    fat_per_100g: float = Field(ge=0)
    fiber_per_100g: float = Field(default=0, ge=0)


class IngredientRead(BaseModel):
    ingredient_id: int
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: float
    nutrition_source: NutritionSource
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
