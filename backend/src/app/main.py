from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin

from app.api import api_router
from app.core.config import settings
from app.core.db_sync import sync_engine
from app.admin.auth import AdminAuth
from app.admin.views import UserAdmin, RecipeAdmin, TagAdmin, IngredientAdmin

app = FastAPI(title="Recipe App", version="0.3.0")

app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret_key)

app.mount("/media", StaticFiles(directory="media"), name="media")
app.mount("/statics", StaticFiles(directory="statics"), name="statics")

app.include_router(api_router)

admin = Admin(
    app=app,
    engine=sync_engine,
    authentication_backend=AdminAuth(secret_key=settings.jwt_secret_key),
    templates_dir="templates",
)

admin.add_view(UserAdmin)
admin.add_view(RecipeAdmin)
admin.add_view(TagAdmin)
admin.add_view(IngredientAdmin)


@app.get("/health")
async def health():
    return {"status": "ok"}