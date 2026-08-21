from fastapi import APIRouter

from app.chat.router import router as chat_router
from app.ingredients.router import router as ingredients_router
from app.meals.router import router as meals_router
from app.notifications.router import router as notifications_router
from app.nutrition.router import router as nutrition_router
from app.recipes.router import router as recipes_router
from app.users.router import router as users_router

api_router = APIRouter()

api_router.include_router(chat_router)
api_router.include_router(users_router)
api_router.include_router(ingredients_router)
api_router.include_router(recipes_router)
api_router.include_router(meals_router)
api_router.include_router(nutrition_router)
api_router.include_router(notifications_router)
