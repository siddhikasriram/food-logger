from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.shared.enums import IngredientPreference


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    height_cm: float | None = Field(default=None, gt=0)
    weight_kg: float | None = Field(default=None, gt=0)
    protein_goal_g: float | None = Field(default=None, ge=0)
    calorie_goal: float | None = Field(default=None, ge=0)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    height_cm: float | None = Field(default=None, gt=0)
    weight_kg: float | None = Field(default=None, gt=0)
    protein_goal_g: float | None = Field(default=None, ge=0)
    calorie_goal: float | None = Field(default=None, ge=0)


class UserRead(BaseModel):
    user_id: int
    name: str
    email: str
    height_cm: float | None
    weight_kg: float | None
    protein_goal_g: float | None
    calorie_goal: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserIngredientPreferenceCreate(BaseModel):
    ingredient_id: int
    preference: IngredientPreference


class UserIngredientPreferenceRead(BaseModel):
    user_id: int
    ingredient_id: int
    preference: IngredientPreference

    model_config = {"from_attributes": True}
