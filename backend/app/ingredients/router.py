from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.ingredients.service import IngredientService

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


def get_ingredient_service(db: Session = Depends(db_session)) -> IngredientService:
    return IngredientService(db)


@router.get("/{ingredient_id}")
def get_ingredient(
    ingredient_id: int, service: IngredientService = Depends(get_ingredient_service)
) -> dict:
    """Fetch a global ingredient. Implementation deferred."""
    _ = (ingredient_id, service)
    raise NotImplementedError("Ingredient endpoints are not implemented in this scaffold.")
