from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.deps import get_current_user, get_optional_user
from app.core.errors import not_found
from app.core.pagination import calc_offset, calc_pages, clamp_size
from app.repositories.recipes import RecipeRepository
from app.schemas.recipes import (
    NutritionOut,
    RecipeCreate,
    RecipeIngredientOut,
    RecipeRead,
    RecipeStepRead,
    RecipeTagOut,
    RecipeUpdate,
)
from app.schemas.recipes_list import RecipeListResponse

router = APIRouter(prefix="/recipes", tags=["recipes"])
repo = RecipeRepository()


def _round2(value: float) -> float:
    return round(value, 2)


async def _to_read(session: AsyncSession, recipe, servings: Optional[int] = None) -> RecipeRead:
    tags = await repo.get_recipe_tags(session, recipe.id)
    ingredients_rows = await repo.get_recipe_ingredients(session, recipe.id)
    steps = await repo.get_recipe_steps(session, recipe.id)

    selected_servings = servings or recipe.base_servings
    ratio = selected_servings / recipe.base_servings if recipe.base_servings else 1

    ingredients = []
    total_calories = 0.0
    total_protein = 0.0
    total_fat = 0.0
    total_carbs = 0.0

    for row in ingredients_rows:
        base_amount = float(row.amount)
        scaled_amount = base_amount * ratio

        calories_per_100g = float(row.calories_per_100g or 0)
        protein_per_100g = float(row.protein_per_100g or 0)
        fat_per_100g = float(row.fat_per_100g or 0)
        carbs_per_100g = float(row.carbs_per_100g or 0)

        if row.unit in ("г", "мл"):
            total_calories += scaled_amount / 100 * calories_per_100g
            total_protein += scaled_amount / 100 * protein_per_100g
            total_fat += scaled_amount / 100 * fat_per_100g
            total_carbs += scaled_amount / 100 * carbs_per_100g

        ingredients.append(
            RecipeIngredientOut(
                id=row.id,
                name=row.name,
                unit=row.unit,
                amount=_round2(scaled_amount),
                base_amount=_round2(base_amount),
            )
        )

    nutrition_total = NutritionOut(
        calories=_round2(total_calories),
        protein=_round2(total_protein),
        fat=_round2(total_fat),
        carbs=_round2(total_carbs),
    )

    nutrition_per_serving = NutritionOut(
        calories=_round2(total_calories / selected_servings) if selected_servings else 0,
        protein=_round2(total_protein / selected_servings) if selected_servings else 0,
        fat=_round2(total_fat / selected_servings) if selected_servings else 0,
        carbs=_round2(total_carbs / selected_servings) if selected_servings else 0,
    )

    return RecipeRead(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        cooking_time_minutes=recipe.cooking_time_minutes,
        base_servings=recipe.base_servings,
        selected_servings=selected_servings,
        tags=[RecipeTagOut(id=t.id, name=t.name, slug=t.slug, color=t.color) for t in tags],
        ingredients=ingredients,
        steps=[
            RecipeStepRead(
                position=step.position,
                text=step.text,
                duration_sec=step.duration_sec,
            )
            for step in steps
        ],
        nutrition_total=nutrition_total,
        nutrition_per_serving=nutrition_per_serving,
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
async def get_recipe(
    recipe_id: int,
    servings: int | None = Query(default=None, ge=1),
    session: AsyncSession = Depends(get_db_session),
):
    recipe = await repo.get(session, recipe_id)
    if recipe is None:
        raise not_found("recipe", recipe_id)
    return await _to_read(session, recipe, servings=servings)


@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    payload: RecipeCreate,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user),
):
    recipe = await repo.create(session, payload, author_id=user.id)
    return await _to_read(session, recipe, servings=recipe.base_servings)


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
    return await _to_read(session, recipe, servings=recipe.base_servings)


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