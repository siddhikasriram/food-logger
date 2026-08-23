from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.schema.ingredient import IngredientCreate, IngredientRead
from app.controller.ingredient import IngredientController
from app.shared.exceptions import NotFoundError

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


def get_ingredient_controller(db: Session = Depends(db_session)) -> IngredientController:
    return IngredientController(db)


@router.get("", response_model=list[IngredientRead])
def list_ingredients(
    controller: IngredientController = Depends(get_ingredient_controller),
) -> list[IngredientRead]:
    return controller.list_ingredients()


@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    payload: IngredientCreate,
    controller: IngredientController = Depends(get_ingredient_controller),
) -> IngredientRead:
    return controller.create_ingredient(payload)


@router.get("/{ingredient_id}", response_model=IngredientRead)
def get_ingredient(
    ingredient_id: int, controller: IngredientController = Depends(get_ingredient_controller)
) -> IngredientRead:
    ingredient = controller.get_ingredient(ingredient_id)
    if ingredient is None:
        raise NotFoundError("Ingredient not found")
    return ingredient
