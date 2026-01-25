from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.favorite import Favorite


class FavoriteRepository:
    async def is_favorite(self, session: AsyncSession, *, user_id: int, recipe_id: int) -> bool:
        res = await session.execute(
            select(Favorite.id).where(Favorite.user_id == user_id, Favorite.recipe_id == recipe_id)
        )
        return res.first() is not None

    async def add(self, session: AsyncSession, *, user_id: int, recipe_id: int) -> Favorite:
        fav = Favorite(user_id=user_id, recipe_id=recipe_id)
        session.add(fav)
        await session.commit()
        await session.refresh(fav)
        return fav

    async def remove(self, session: AsyncSession, *, user_id: int, recipe_id: int) -> bool:
        res = await session.execute(
            select(Favorite).where(Favorite.user_id == user_id, Favorite.recipe_id == recipe_id)
        )
        fav = res.scalars().first()
        if fav is None:
            return False

        session.delete(fav)
        await session.commit()
        return True

    async def list_recipe_ids(self, session: AsyncSession, *, user_id: int) -> List[int]:
        res = await session.execute(select(Favorite.recipe_id).where(Favorite.user_id == user_id))
        return [row[0] for row in res.all()]