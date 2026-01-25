from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.deps import require_admin
from app.core.errors import not_found
from app.repositories.ingredients import IngredientRepository
from app.schemas.ingredients import IngredientCreate, IngredientRead, IngredientUpdate

router = APIRouter(prefix="/ingredients", tags=["ingredients"])
repo = IngredientRepository()


@router.get("", response_model=List[IngredientRead])
async def list_ingredients(
    session: AsyncSession = Depends(get_db_session),
    search: str | None = Query(default=None, max_length=120),
):
    items = await repo.list(session, search=search)
    return [IngredientRead(id=i.id, name=i.name, unit=i.unit) for i in items]


@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
async def create_ingredient(
    payload: IngredientCreate,
    session: AsyncSession = Depends(get_db_session),
    _admin=Depends(require_admin),
):
    ing = await repo.create(session, payload)
    return IngredientRead(id=ing.id, name=ing.name, unit=ing.unit)


@router.get("/{ingredient_id}", response_model=IngredientRead)
async def get_ingredient(
    ingredient_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    ing = await repo.get(session, ingredient_id)
    if not ing:
        raise not_found("ingredient", ingredient_id)
    return IngredientRead(id=ing.id, name=ing.name, unit=ing.unit)


@router.patch("/{ingredient_id}", response_model=IngredientRead)
async def update_ingredient(
    ingredient_id: int,
    payload: IngredientUpdate,
    session: AsyncSession = Depends(get_db_session),
    _admin=Depends(require_admin),
):
    ing = await repo.get(session, ingredient_id)
    if not ing:
        raise not_found("ingredient", ingredient_id)
    ing = await repo.update(session, ing, payload)
    return IngredientRead(id=ing.id, name=ing.name, unit=ing.unit)


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(
    ingredient_id: int,
    session: AsyncSession = Depends(get_db_session),
    _admin=Depends(require_admin),
):
    ing = await repo.get(session, ingredient_id)
    if not ing:
        raise not_found("ingredient", ingredient_id)
    await repo.delete(session, ing)
    return None