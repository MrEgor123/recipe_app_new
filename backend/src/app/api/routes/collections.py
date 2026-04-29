from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.deps import get_current_user
from app.models.user import User
from app.repositories.collections import CollectionRepository
from app.repositories.recipes import RecipeRepository
from app.schemas.collections import (
    CollectionCreate,
    CollectionOut,
    CollectionRecipeCardOut,
    CollectionRecipeIdsOut,
    CollectionUpdate,
    RecipeCollectionsUpdate,
)
from app.schemas.recipes import (
    NutritionOut,
    RecipeIngredientOut,
    RecipeRead,
    RecipeStepRead,
    RecipeTagOut,
)

router = APIRouter(prefix="/collections", tags=["collections"])
recipe_collections_router = APIRouter(prefix="/recipes", tags=["collections"])

collection_repo = CollectionRepository()
recipe_repo = RecipeRepository()


def _round2(value: float) -> float:
    return round(value, 2)


def serialize_collection(collection, recipes_count: int) -> CollectionOut:
    return CollectionOut(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        recipes_count=recipes_count,
        created_at=collection.created_at,
    )


async def _to_recipe_read(
    session: AsyncSession,
    recipe,
    servings: int | None = None,
) -> RecipeRead:
    tags = await recipe_repo.get_recipe_tags(session, recipe.id)
    ingredients_rows = await recipe_repo.get_recipe_ingredients(session, recipe.id)
    steps = await recipe_repo.get_recipe_steps(session, recipe.id)

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


def _to_collection_recipe_card(recipe) -> CollectionRecipeCardOut:
    return CollectionRecipeCardOut(
        id=recipe.id,
        title=recipe.title,
        image=getattr(recipe, "image", None),
        cooking_time_minutes=recipe.cooking_time_minutes,
        rating_avg=float(getattr(recipe, "rating_avg", 0) or 0),
        rating_count=int(getattr(recipe, "rating_count", 0) or 0),
    )


@router.post("/", response_model=CollectionOut, status_code=status.HTTP_201_CREATED)
async def create_collection(
    payload: CollectionCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    try:
        collection = await collection_repo.create_collection(
            session,
            user_id=current_user.id,
            name=payload.name,
            description=payload.description,
        )
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Подборка с таким названием уже существует",
        )

    row = await collection_repo.get_user_collection_with_count(
        session,
        user_id=current_user.id,
        collection_id=collection.id,
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подборка не найдена",
        )

    collection_obj, recipes_count = row
    return serialize_collection(collection_obj, recipes_count)


@router.get("/", response_model=list[CollectionOut])
async def get_my_collections(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    rows = await collection_repo.get_user_collections(session, user_id=current_user.id)
    return [serialize_collection(collection, recipes_count) for collection, recipes_count in rows]


@router.get("/{collection_id}/", response_model=CollectionOut)
async def get_collection(
    collection_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    row = await collection_repo.get_user_collection_with_count(
        session,
        user_id=current_user.id,
        collection_id=collection_id,
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подборка не найдена",
        )

    collection, recipes_count = row
    return serialize_collection(collection, recipes_count)


@router.patch("/{collection_id}/", response_model=CollectionOut)
async def update_collection(
    collection_id: int,
    payload: CollectionUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    collection = await collection_repo.get_user_collection(
        session,
        user_id=current_user.id,
        collection_id=collection_id,
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подборка не найдена",
        )

    try:
        await collection_repo.update_collection(
            session,
            collection=collection,
            name=payload.name,
            description=payload.description,
        )
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Подборка с таким названием уже существует",
        )

    row = await collection_repo.get_user_collection_with_count(
        session,
        user_id=current_user.id,
        collection_id=collection_id,
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подборка не найдена",
        )

    collection_obj, recipes_count = row
    return serialize_collection(collection_obj, recipes_count)


@router.delete("/{collection_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    collection = await collection_repo.get_user_collection(
        session,
        user_id=current_user.id,
        collection_id=collection_id,
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подборка не найдена",
        )

    await collection_repo.delete_collection(session, collection=collection)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{collection_id}/recipes/", response_model=list[CollectionRecipeCardOut])
async def get_collection_recipes(
    collection_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    collection = await collection_repo.get_user_collection(
        session,
        user_id=current_user.id,
        collection_id=collection_id,
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подборка не найдена",
        )

    recipes = await collection_repo.get_collection_recipes(
        session,
        collection_id=collection_id,
    )
    return [_to_collection_recipe_card(recipe) for recipe in recipes]


@router.post(
    "/{collection_id}/recipes/{recipe_id}/",
    status_code=status.HTTP_201_CREATED,
)
async def add_recipe_to_collection(
    collection_id: int,
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    collection = await collection_repo.get_user_collection(
        session,
        user_id=current_user.id,
        collection_id=collection_id,
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подборка не найдена",
        )

    recipe = await recipe_repo.get(session, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецепт не найден",
        )

    exists = await collection_repo.collection_has_recipe(
        session,
        collection_id=collection_id,
        recipe_id=recipe_id,
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Рецепт уже добавлен в подборку",
        )

    await collection_repo.add_recipe_to_collection(
        session,
        collection_id=collection_id,
        recipe_id=recipe_id,
    )
    return {"detail": "Рецепт добавлен в подборку"}


@router.delete(
    "/{collection_id}/recipes/{recipe_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_recipe_from_collection(
    collection_id: int,
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    collection = await collection_repo.get_user_collection(
        session,
        user_id=current_user.id,
        collection_id=collection_id,
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подборка не найдена",
        )

    await collection_repo.remove_recipe_from_collection(
        session,
        collection_id=collection_id,
        recipe_id=recipe_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@recipe_collections_router.get(
    "/{recipe_id}/collections/",
    response_model=CollectionRecipeIdsOut,
)
async def get_recipe_collections(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    recipe = await recipe_repo.get(session, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецепт не найден",
        )

    collection_ids = await collection_repo.get_recipe_collection_ids_for_user(
        session,
        user_id=current_user.id,
        recipe_id=recipe_id,
    )
    return CollectionRecipeIdsOut(collection_ids=collection_ids)


@recipe_collections_router.put(
    "/{recipe_id}/collections/",
    response_model=CollectionRecipeIdsOut,
)
async def update_recipe_collections(
    recipe_id: int,
    payload: RecipeCollectionsUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    recipe = await recipe_repo.get(session, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецепт не найден",
        )

    collection_ids = await collection_repo.replace_recipe_collections_for_user(
        session,
        user_id=current_user.id,
        recipe_id=recipe_id,
        collection_ids=payload.collection_ids,
    )
    return CollectionRecipeIdsOut(collection_ids=collection_ids)