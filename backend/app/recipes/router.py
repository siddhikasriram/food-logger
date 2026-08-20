from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.recipes.service import RecipeService

router = APIRouter(prefix="/recipes", tags=["recipes"])


def get_recipe_service(db: Session = Depends(db_session)) -> RecipeService:
    return RecipeService(db)


@router.get("/{recipe_id}")
def get_recipe(recipe_id: int, service: RecipeService = Depends(get_recipe_service)) -> dict:
    """Fetch a global recipe. Implementation deferred."""
    _ = (recipe_id, service)
    raise NotImplementedError("Recipe endpoints are not implemented in this scaffold.")
