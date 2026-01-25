from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.deps import get_current_user
from app.core.errors import not_found
from app.core.pagination import calc_offset, calc_pages, clamp_size
from app.models.recipe import Recipe
from app.models.user import User
from app.repositories.recipes import RecipeRepository
from app.repositories.subscriptions import SubscriptionRepository
from app.schemas.recipes import RecipeIngredientOut, RecipeRead, RecipeTagOut
from app.schemas.recipes_list import RecipeListResponse

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
sub_repo = SubscriptionRepository()
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


@router.get("", response_model=List[dict])
async def list_subscriptions(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    author_ids = await sub_repo.list_author_ids(session, user_id=user.id)
    if not author_ids:
        return []
    res = await session.execute(select(User).where(User.id.in_(author_ids)).order_by(User.username.asc()))
    authors = res.scalars().all()
    return [{"id": a.id, "username": a.username, "email": a.email} for a in authors]


@router.post("/users/{author_id}/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe(
    author_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    if author_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot subscribe to yourself")

    author = await session.get(User, author_id)
    if author is None:
        raise not_found("user", author_id)

    if await sub_repo.is_subscribed(session, user_id=user.id, author_id=author_id):
        return {"status": "already_subscribed"}

    await sub_repo.add(session, user_id=user.id, author_id=author_id)
    return {"status": "subscribed"}


@router.delete("/users/{author_id}/subscribe", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe(
    author_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    author = await session.get(User, author_id)
    if author is None:
        raise not_found("user", author_id)

    await sub_repo.remove(session, user_id=user.id, author_id=author_id)
    return None


@router.get("/feed", response_model=RecipeListResponse)
async def subscriptions_feed(
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
):
    author_ids = await sub_repo.list_author_ids(session, user_id=user.id)
    if not author_ids:
        return RecipeListResponse(items=[], page=page, size=clamp_size(size), total=0, pages=0)

    size = clamp_size(size)
    offset = calc_offset(page, size)

    total_stmt = select(func.count(Recipe.id)).where(Recipe.author_id.in_(author_ids))
    total = int((await session.execute(total_stmt)).scalar_one())
    pages = calc_pages(total, size)

    stmt = (
        select(Recipe)
        .where(Recipe.author_id.in_(author_ids))
        .order_by(Recipe.id.desc())
        .limit(size)
        .offset(offset)
    )
    recipes = (await session.execute(stmt)).scalars().all()
    items = [await _to_read(session, r) for r in recipes]

    return RecipeListResponse(items=items, page=page, size=size, total=total, pages=pages)
