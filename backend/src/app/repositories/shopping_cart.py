from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shopping_cart import ShoppingCartItem


class ShoppingCartRepository:
    async def is_in_cart(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        recipe_id: int,
    ) -> bool:
        res = await session.execute(
            select(ShoppingCartItem.id).where(
                ShoppingCartItem.user_id == user_id,
                ShoppingCartItem.recipe_id == recipe_id,
            )
        )
        return res.first() is not None

    async def add(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        recipe_id: int,
    ) -> ShoppingCartItem:
        item = ShoppingCartItem(user_id=user_id, recipe_id=recipe_id)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item

    async def remove(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        recipe_id: int,
    ) -> bool:
        res = await session.execute(
            select(ShoppingCartItem).where(
                ShoppingCartItem.user_id == user_id,
                ShoppingCartItem.recipe_id == recipe_id,
            )
        )
        item = res.scalars().first()
        if item is None:
            return False

        await session.delete(item)
        await session.commit()
        return True

    async def list_recipe_ids(
        self,
        session: AsyncSession,
        *,
        user_id: int,
    ) -> List[int]:
        res = await session.execute(
            select(ShoppingCartItem.recipe_id).where(
                ShoppingCartItem.user_id == user_id
            )
        )
        return [row[0] for row in res.all()]

    async def get_count(
        self,
        session: AsyncSession,
        *,
        user_id: int,
    ) -> int:
        res = await session.execute(
            select(func.count(ShoppingCartItem.id)).where(
                ShoppingCartItem.user_id == user_id
            )
        )
        return int(res.scalar() or 0)