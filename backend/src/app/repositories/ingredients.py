from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingredient import Ingredient
from app.schemas.ingredients import IngredientCreate, IngredientUpdate


class IngredientRepository:
    async def list(self, session: AsyncSession, search: str | None = None) -> List[Ingredient]:
        stmt = select(Ingredient).order_by(Ingredient.id.asc())
        if search:
            stmt = stmt.where(Ingredient.name.contains(search))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def search(self, session: AsyncSession, *, search: str | None = None) -> List[Ingredient]:
        # alias for Foodgram frontend (name= query param)
        return await self.list(session, search=search)
    
    async def get(self, session: AsyncSession, ingredient_id: int) -> Ingredient | None:
        result = await session.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
        return result.scalars().first()
    
    async def create(self, session: AsyncSession, payload: IngredientCreate) -> Ingredient:
        ing = Ingredient(
            name=payload.name,
            unit=payload.unit,
        )
        session.add(ing)
        await session.commit()
        await session.refresh(ing)
        return ing
    
    async def update(self, session: AsyncSession, ing: Ingredient, payload: IngredientUpdate) -> Ingredient:
        data = payload.model_dump(exclude_unset=True)

        for k, v in data.items():
            setattr(ing, k, v)
        await session.commit()
        await session.refresh(ing)
        return ing
    
    async def delete(self, session: AsyncSession, ing: Ingredient) -> None:
        await session.delete(ing)
        await session.commit()
