from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.recipes.schemas import RecipeCreate, RecipeRead
from app.recipes.service import RecipeService
from app.shared.exceptions import NotFoundError

router = APIRouter(prefix="/recipes", tags=["recipes"])


def get_recipe_service(db: Session = Depends(db_session)) -> RecipeService:
    return RecipeService(db)


@router.get("", response_model=list[RecipeRead])
def list_recipes(service: RecipeService = Depends(get_recipe_service)) -> list[RecipeRead]:
    return service.list_recipes()


@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(
    payload: RecipeCreate, service: RecipeService = Depends(get_recipe_service)
) -> RecipeRead:
    return service.create_recipe(payload)


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(recipe_id: int, service: RecipeService = Depends(get_recipe_service)) -> RecipeRead:
    recipe = service.get_recipe(recipe_id)
    if recipe is None:
        raise NotFoundError("Recipe not found")
    return recipe
