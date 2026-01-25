from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.errors import not_found
from app.repositories.recipes import RecipeRepository
from app.repositories.short_links import ShortLinkRepository
from app.schemas.recipes import RecipeIngredientOut, RecipeRead, RecipeTagOut

router = APIRouter(tags=["short-links"])
recipes_repo = RecipeRepository()
links_repo = ShortLinkRepository()


async def _to_read(session: AsyncSession, recipe) -> RecipeRead:
    tags = await recipes_repo.get_recipe_tags(session, recipe.id)
    ingredients_rows = await recipes_repo.get_recipe_ingredients(session, recipe.id)

    return RecipeRead(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        cooking_time_minutes=recipe.cooking_time_minutes,
        tags=[RecipeTagOut(id=t.id, name=t.name, slug=t.slug, color=t.color) for t in tags],
        ingredients=[
            RecipeIngredientOut(id=row.id, name=row.name, unit=row.unit, amount=float(row.amount))
            for row in ingredients_rows
        ],
    )


@router.post("/recipes/{recipe_id}/short-link")
async def get_or_create_short_link(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    recipe = await recipes_repo.get(session, recipe_id)
    if recipe is None:
        raise not_found("recipe", recipe_id)

    existing = await links_repo.get_by_recipe(session, recipe_id)
    if existing is not None:
        return {"code": existing.code, "url": f"/s/{existing.code}"}

    created = await links_repo.create_for_recipe(session, recipe_id)
    return {"code": created.code, "url": f"/s/{created.code}"}


@router.get("/s/{code}")
async def open_short_link(
    code: str,
    session: AsyncSession = Depends(get_db_session),
):
    link = await links_repo.get_by_code(session, code)
    if link is None:
        raise not_found("short_link", 0)

    recipe = await recipes_repo.get(session, link.recipe_id)
    if recipe is None:
        raise not_found("recipe", link.recipe_id)

    # Redirect to the frontend recipe page; nginx serves the SPA.
    return RedirectResponse(url=f"/recipes/{recipe.id}", status_code=307)