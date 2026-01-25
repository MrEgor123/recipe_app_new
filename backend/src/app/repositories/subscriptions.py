from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription


class SubscriptionRepository:
    async def is_subscribed(self, session: AsyncSession, *, user_id: int, author_id: int) -> bool:
        res = await session.execute(
            select(Subscription.id).where(
                Subscription.user_id == user_id,
                Subscription.author_id == author_id,
            )
        )
        return res.first() is not None

    async def add(self, session: AsyncSession, *, user_id: int, author_id: int) -> Subscription:
        sub = Subscription(user_id=user_id, author_id=author_id)
        session.add(sub)
        await session.commit()
        await session.refresh(sub)
        return sub

    async def remove(self, session: AsyncSession, *, user_id: int, author_id: int) -> bool:
        res = await session.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.author_id == author_id,
            )
        )
        sub = res.scalars().first()
        if sub is None:
            return False

        await session.delete(sub)  # <-- ВАЖНО: delete() тут await
        await session.commit()
        return True

    async def list_author_ids(self, session: AsyncSession, *, user_id: int) -> List[int]:
        res = await session.execute(select(Subscription.author_id).where(Subscription.user_id == user_id))
        return [row[0] for row in res.all()]
