from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.schemas.tags import TagCreate, TagUpdate


class TagRepository:
    async def list(self, session: AsyncSession) -> List[Tag]:
        result = await session.execute(select(Tag).order_by(Tag.id.asc()))
        return list(result.scalars().all())
    
    async def get(self, session: AsyncSession, tag_id: int) -> Tag | None:
        result = await session.execute(select(Tag).where(Tag.id == tag_id))
        return result.scalars().first()
    
    async def create(self, session: AsyncSession, payload: TagCreate) -> Tag:
        tag = Tag(
            name=payload.name,
            slug=payload.slug,
            color=payload.color,
        )
        session.add(tag)
        await session.commit()
        await session.refresh(tag)
        return tag
    
    async def update(self, session: AsyncSession, tag: Tag, payload: TagUpdate) -> Tag:
        data = payload.model_dump(exclude_unset=True)

        for k, v in data.items():
            setattr(tag, k, v)
        await session.commit()
        await session.refresh(tag)
        return tag
    
    async def delete(self, session: AsyncSession, tag: Tag) -> None:
        await session.delete(tag)
        await session.commit()

    async def get_by_slugs(self, session: AsyncSession, *, slugs: List[str]) -> List[Tag]:
        if not slugs:
            return []
        res = await session.execute(select(Tag).where(Tag.slug.in_(slugs)))
        return list(res.scalars().all())
