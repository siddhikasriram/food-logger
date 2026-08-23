from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import db_session
from app.schema.recipe import RecipeCreate, RecipeRead
from app.controller.recipe import RecipeController
from app.shared.exceptions import NotFoundError

router = APIRouter(prefix="/recipes", tags=["recipes"])


def get_recipe_controller(db: Session = Depends(db_session)) -> RecipeController:
    return RecipeController(db)


@router.get("", response_model=list[RecipeRead])
def list_recipes(controller: RecipeController = Depends(get_recipe_controller)) -> list[RecipeRead]:
    return controller.list_recipes()


@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(
    payload: RecipeCreate, controller: RecipeController = Depends(get_recipe_controller)
) -> RecipeRead:
    return controller.create_recipe(payload)


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(recipe_id: int, controller: RecipeController = Depends(get_recipe_controller)) -> RecipeRead:
    recipe = controller.get_recipe(recipe_id)
    if recipe is None:
        raise NotFoundError("Recipe not found")
    return recipe
