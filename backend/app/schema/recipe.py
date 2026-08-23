from datetime import datetime

from pydantic import BaseModel, Field


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity_g: float = Field(gt=0)


class RecipeIngredientRead(BaseModel):
    recipe_id: int
    ingredient_id: int
    quantity_g: float

    model_config = {"from_attributes": True}


class RecipeIngredientDetail(BaseModel):
    ingredient_id: int
    name: str
    quantity_g: float


class RecipeTagRead(BaseModel):
    tag_id: int
    name: str

    model_config = {"from_attributes": True}


class RecipeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    instructions: str | None = None
    servings: float = Field(default=1, gt=0)
    created_by: int | None = None
    ingredients: list[RecipeIngredientCreate] = Field(default_factory=list)
    tag_ids: list[int] = Field(default_factory=list)


class RecipeRead(BaseModel):
    recipe_id: int
    name: str
    description: str | None
    instructions: str | None
    servings: float
    created_by: int | None
    created_at: datetime
    updated_at: datetime
    ingredients: list[RecipeIngredientDetail] = Field(default_factory=list)
    tags: list[RecipeTagRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}
