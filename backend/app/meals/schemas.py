from datetime import datetime

from pydantic import BaseModel, Field

from app.shared.enums import MealType


class MealLogCreate(BaseModel):
    user_id: int
    recipe_id: int
    meal_type: MealType
    servings: float = Field(gt=0)
    consumed_at: datetime


class MealLogRead(BaseModel):
    meal_log_id: int
    user_id: int
    recipe_id: int
    meal_type: MealType
    servings: float
    consumed_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
