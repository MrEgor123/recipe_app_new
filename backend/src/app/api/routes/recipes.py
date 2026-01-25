from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.deps import get_current_user, get_optional_user
from app.core.errors import not_found
from app.core.pagination import calc_offset, calc_pages, clamp_size
from app.repositories.recipes import RecipeRepository
from app.schemas.recipes import (
    RecipeCreate,
    RecipeIngredientOut,
    RecipeRead,
    RecipeTagOut,
    RecipeUpdate,
)
from app.schemas.recipes_list import RecipeListResponse

router = APIRouter(prefix="/recipes", tags=["recipes"])
repo = RecipeRepository()


async def _to_read(session: AsyncSession, recipe) -> RecipeRead:
    tags = await repo.get_recipe_tags(session, recipe.id)
    ingredients_rows = await repo.get_recipe_ingredients(session, recipe.id)

    return RecipeRead(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        cooking_time_minutes=recipe.cooking_time_minutes,
        tags=[RecipeTagOut(id=t.id, name=t.name, slug=t.slug, color=t.color) for t in tags],
        ingredients=[
            RecipeIngredientOut(
                id=row.id,
                name=row.name,
                unit=row.unit,
                amount=float(row.amount),
            )
            for row in ingredients_rows
        ],
    )


@router.get("", response_model=RecipeListResponse)
async def list_recipes(
    session: AsyncSession = Depends(get_db_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=50),
    author_id: Optional[int] = Query(default=None, ge=1),
    tag_ids: Optional[List[int]] = Query(default=None),
    is_favorited: bool = Query(default=False),
    is_in_shopping_cart: bool = Query(default=False),
    user_opt=Depends(get_optional_user),
):
    # вариант A: если пользователь хочет фильтры по избранному/корзине — он должен быть авторизован
    if (is_favorited or is_in_shopping_cart) and user_opt is None:
        raise HTTPException(status_code=401, detail="Authentication required for this filter")

    user_id = user_opt.id if user_opt else None

    size = clamp_size(size)
    offset = calc_offset(page, size)

    total = await repo.count_filtered(
        session,
        author_id=author_id,
        tag_ids=tag_ids,
        user_id=user_id,
        is_favorited=is_favorited,
        is_in_shopping_cart=is_in_shopping_cart,
    )
    pages = calc_pages(total, size)

    recipes = await repo.list_filtered(
        session,
        author_id=author_id,
        tag_ids=tag_ids,
        limit=size,
        offset=offset,
        user_id=user_id,
        is_favorited=is_favorited,
        is_in_shopping_cart=is_in_shopping_cart,
    )

    items = [await _to_read(session, r) for r in recipes]
    return RecipeListResponse(items=items, page=page, size=size, total=total, pages=pages)


@router.get("/{recipe_id}", response_model=RecipeRead)
async def get_recipe(recipe_id: int, session: AsyncSession = Depends(get_db_session)):
    recipe = await repo.get(session, recipe_id)
    if recipe is None:
        raise not_found("recipe", recipe_id)
    return await _to_read(session, recipe)


@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    payload: RecipeCreate,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    recipe = await repo.create(session, payload, author_id=user.id)
    return await _to_read(session, recipe)


@router.patch("/{recipe_id}", response_model=RecipeRead)
async def update_recipe(
    recipe_id: int,
    payload: RecipeUpdate,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    recipe = await repo.get(session, recipe_id)
    if recipe is None:
        raise not_found("recipe", recipe_id)

    if (recipe.author_id != user.id) and (not user.is_admin):
        raise HTTPException(status_code=403, detail="Forbidden")

    recipe = await repo.update(session, recipe, payload)
    return await _to_read(session, recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    recipe = await repo.get(session, recipe_id)
    if recipe is None:
        raise not_found("recipe", recipe_id)

    if (recipe.author_id != user.id) and (not user.is_admin):
        raise HTTPException(status_code=403, detail="Forbidden")

    await repo.delete(session, recipe)
    return None
