from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.deps import require_admin
from app.core.errors import not_found
from app.repositories.tags import TagRepository
from app.schemas.tags import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])
repo = TagRepository()


@router.get("", response_model=List[TagRead])
async def list_tags(session: AsyncSession = Depends(get_db_session)):
    tags = await repo.list(session)
    return [TagRead(id=t.id, name=t.name, slug=t.slug, color=t.color) for t in tags]


@router.get("/{tag_id}", response_model=TagRead)
async def get_tag(tag_id: int, session: AsyncSession = Depends(get_db_session)):
    tag = await repo.get(session, tag_id)
    if tag is None:
        raise not_found("tag", tag_id)
    return TagRead(id=tag.id, name=tag.name, slug=tag.slug, color=tag.color)


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(
    payload: TagCreate,
    session: AsyncSession = Depends(get_db_session),
    _admin=Depends(require_admin),
):
    t = await repo.create(session, payload)
    return TagRead(id=t.id, name=t.name, slug=t.slug, color=t.color)


@router.patch("/{tag_id}", response_model=TagRead)
async def update_tag(
    tag_id: int,
    payload: TagUpdate,
    session: AsyncSession = Depends(get_db_session),
    _admin=Depends(require_admin),
):
    t = await repo.get(session, tag_id)
    if not t:
        raise not_found("tag", tag_id)
    t = await repo.update(session, t, payload)
    return TagRead(id=t.id, name=t.name, slug=t.slug, color=t.color)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    session: AsyncSession = Depends(get_db_session),
    _admin=Depends(require_admin),
):
    t = await repo.get(session, tag_id)
    if t is None:
        raise not_found("tag", tag_id)
    await repo.delete(session, t)
    return None