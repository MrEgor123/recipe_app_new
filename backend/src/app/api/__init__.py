from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.recipes import router as recipes_router
from app.api.routes.tags import router as tags_router
from app.api.routes.ingredients import router as ingredients_router
from app.api.routes.favorites import router as favorites_router
from app.api.routes.subscriptions import router as subscriptions_router
from app.api.routes.shopping_cart import router as shopping_cart_router
from app.api.routes.short_links import router as short_links_router
from app.api.routes.foodgram import router as foodgram_router
from app.api.routes.comments import router as comments_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(recipes_router)
api_router.include_router(tags_router)
api_router.include_router(ingredients_router)
api_router.include_router(favorites_router)
api_router.include_router(subscriptions_router)
api_router.include_router(shopping_cart_router)
api_router.include_router(short_links_router)
api_router.include_router(foodgram_router)
api_router.include_router(comments_router)