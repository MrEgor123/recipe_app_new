from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.deps import get_current_user
from app.core.pagination import calc_offset, calc_pages, clamp_size
from app.models.favorite import Favorite
from app.models.recipe import Recipe
from app.repositories.recipes import RecipeRepository
from app.schemas.recipes import RecipeIngredientOut, RecipeRead, RecipeTagOut
from app.schemas.recipes_list import RecipeListResponse

router = APIRouter(tags=["favorites"])
recipe_repo = RecipeRepository()


async def _to_read(session: AsyncSession, recipe: Recipe) -> RecipeRead:
    tags = await recipe_repo.get_recipe_tags(session, recipe.id)
    ingredients_rows = await recipe_repo.get_recipe_ingredients(session, recipe.id)
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


@router.get("/favorites", response_model=RecipeListResponse)
async def list_favorites(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
):
    size = clamp_size(size)
    offset = calc_offset(page, size)

    total_stmt = select(func.count(Favorite.id)).where(Favorite.user_id == user.id)
    total = int((await session.execute(total_stmt)).scalar_one())
    pages = calc_pages(total, size)

    stmt = (
        select(Recipe)
        .join(Favorite, Favorite.recipe_id == Recipe.id)
        .where(Favorite.user_id == user.id)
        .order_by(Recipe.id.desc())
        .limit(size)
        .offset(offset)
    )
    recipes = (await session.execute(stmt)).scalars().all()
    items = [await _to_read(session, r) for r in recipes]

    return RecipeListResponse(items=items, page=page, size=size, total=total, pages=pages)


@router.post("/recipes/{recipe_id}/favorite", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    # idempotent add
    exists_stmt = select(Favorite.id).where(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id)
    if (await session.execute(exists_stmt)).first() is not None:
        return {"status": "already_favorite"}

    session.add(Favorite(user_id=user.id, recipe_id=recipe_id))
    await session.commit()
    return {"status": "added"}


@router.delete("/recipes/{recipe_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    stmt = select(Favorite).where(Favorite.user_id == user.id, Favorite.recipe_id == recipe_id)
    fav = (await session.execute(stmt)).scalars().first()
    if fav is not None:
        await session.delete(fav)
        await session.commit()
    return None
