import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.short_link import ShortLink


class ShortLinkRepository:
    async def get_by_recipe(self, session: AsyncSession, recipe_id: int) -> ShortLink | None:
        res = await session.execute(select(ShortLink).where(ShortLink.recipe_id == recipe_id))
        return res.scalars().first()

    async def get_by_code(self, session: AsyncSession, code: str) -> ShortLink | None:
        res = await session.execute(select(ShortLink).where(ShortLink.code == code))
        return res.scalars().first()

    async def create_for_recipe(self, session: AsyncSession, recipe_id: int) -> ShortLink:
        # генерируем уникальный код
        while True:
            code = secrets.token_urlsafe(6)[:10]
            exists = await self.get_by_code(session, code)
            if exists is None:
                break

        link = ShortLink(recipe_id=recipe_id, code=code)
        session.add(link)
        await session.commit()
        await session.refresh(link)
        return link

    async def get_or_create(self, session: AsyncSession, *, recipe_id: int) -> ShortLink:
        existing = await self.get_by_recipe(session, recipe_id)
        if existing is not None:
            return existing
        return await self.create_for_recipe(session, recipe_id=recipe_id)
