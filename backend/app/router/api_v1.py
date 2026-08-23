from fastapi import APIRouter

from app.router.chat import router as chat_router
from app.router.ingredient import router as ingredients_router
from app.router.meal import router as meals_router
from app.router.notification import router as notifications_router
from app.router.nutrition import router as nutrition_router
from app.router.ontology import router as ontology_router
from app.router.recipe import router as recipes_router
from app.router.user import router as users_router

api_router = APIRouter()

api_router.include_router(chat_router)
api_router.include_router(users_router)
api_router.include_router(ingredients_router)
api_router.include_router(recipes_router)
api_router.include_router(meals_router)
api_router.include_router(nutrition_router)
api_router.include_router(notifications_router)
api_router.include_router(ontology_router)
