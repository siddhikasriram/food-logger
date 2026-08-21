from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.ingredients.schemas import IngredientCreate, IngredientRead
from app.ingredients.service import IngredientService
from app.shared.exceptions import NotFoundError

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


def get_ingredient_service(db: Session = Depends(db_session)) -> IngredientService:
    return IngredientService(db)


@router.get("", response_model=list[IngredientRead])
def list_ingredients(
    service: IngredientService = Depends(get_ingredient_service),
) -> list[IngredientRead]:
    return service.list_ingredients()


@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    payload: IngredientCreate,
    service: IngredientService = Depends(get_ingredient_service),
) -> IngredientRead:
    return service.create_ingredient(payload)


@router.get("/{ingredient_id}", response_model=IngredientRead)
def get_ingredient(
    ingredient_id: int, service: IngredientService = Depends(get_ingredient_service)
) -> IngredientRead:
    ingredient = service.get_ingredient(ingredient_id)
    if ingredient is None:
        raise NotFoundError("Ingredient not found")
    return ingredient
