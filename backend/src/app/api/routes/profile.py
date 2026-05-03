from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.deps import get_current_user, get_optional_user
from app.models.user import User
from app.repositories.collections import CollectionRepository
from app.repositories.comments import CommentRepository
from app.repositories.profile import ProfileRepository
from app.schemas.collections import CollectionOut
from app.schemas.comments import ProfileCommentOut
from app.schemas.profile import (
    ProfileRecipeOut,
    ProfileStatsOut,
    UserProfileOut,
    UserProfileUpdate,
    UserReportCreate,
    UserReportOut,
)

router = APIRouter(prefix="/users", tags=["profile"])

repo = ProfileRepository()
collections_repo = CollectionRepository()
comments_repo = CommentRepository()


async def _build_profile(
    session: AsyncSession,
    target_user: User,
    current_user: User | None,
) -> UserProfileOut:
    is_owner = current_user is not None and current_user.id == target_user.id
    is_subscribed = False

    if current_user is not None and not is_owner:
        is_subscribed = await repo.is_subscribed(
            session=session,
            current_user_id=current_user.id,
            target_user_id=target_user.id,
        )

    is_blocked = target_user.is_profile_blocked
    can_view_private_blocked_profile = (
        is_owner or (current_user is not None and current_user.is_admin)
    )

    if is_blocked and not can_view_private_blocked_profile:
        stats = {
            "recipes_count": 0,
            "followers_count": 0,
            "following_count": 0,
            "comments_count": 0,
            "collections_count": 0,
            "total_recipe_likes": 0,
        }
        recipes = []
        status_text = None
        bio_text = None
    else:
        stats = await repo.get_stats(session=session, user_id=target_user.id)
        recipes = await repo.get_user_recipes(session=session, user_id=target_user.id)
        status_text = target_user.status
        bio_text = target_user.bio

    return UserProfileOut(
        id=target_user.id,
        email=target_user.email,
        username=target_user.username,
        first_name=target_user.first_name,
        last_name=target_user.last_name,
        avatar=target_user.avatar,
        cover_image=target_user.cover_image,
        status=status_text,
        bio=bio_text,
        created_at=target_user.created_at,
        is_subscribed=is_subscribed,
        is_owner=is_owner,
        is_admin=bool(target_user.is_admin),
        is_blocked=is_blocked,
        blocked_until=target_user.blocked_until,
        block_reason=target_user.block_reason,
        stats=ProfileStatsOut(**stats),
        recipes=[ProfileRecipeOut(**recipe) for recipe in recipes],
    )


@router.get("/me/profile/", response_model=UserProfileOut)
async def get_my_profile(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    return await _build_profile(
        session=session,
        target_user=current_user,
        current_user=current_user,
    )


@router.patch("/me/profile/", response_model=UserProfileOut)
async def update_my_profile(
    payload: UserProfileUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    allowed_fields = {"status", "bio", "cover_image"}

    updates = {
        field_name: getattr(payload, field_name)
        for field_name in payload.model_fields_set
        if field_name in allowed_fields
    }

    if updates:
        current_user = await repo.update_profile(
            session=session,
            user=current_user,
            updates=updates,
        )

    return await _build_profile(
        session=session,
        target_user=current_user,
        current_user=current_user,
    )


@router.get("/me/collections/", response_model=list[CollectionOut])
async def get_my_profile_collections(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    rows = await collections_repo.get_user_collections(
        session=session,
        user_id=current_user.id,
    )

    return [
        CollectionOut(
            id=collection.id,
            name=collection.name,
            description=collection.description,
            recipes_count=recipes_count,
            created_at=collection.created_at,
        )
        for collection, recipes_count in rows
    ]


@router.get("/me/comments/", response_model=list[ProfileCommentOut])
async def get_my_profile_comments(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    rows = await comments_repo.list_by_user(
        session=session,
        user_id=current_user.id,
        current_user_id=current_user.id,
    )

    return [ProfileCommentOut(**row) for row in rows]


@router.get("/{user_id}/profile/", response_model=UserProfileOut)
async def get_user_profile(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User | None = Depends(get_optional_user),
):
    target_user = await repo.get_user_by_id(session=session, user_id=user_id)

    if target_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return await _build_profile(
        session=session,
        target_user=target_user,
        current_user=current_user,
    )


@router.post(
    "/{user_id}/report/",
    response_model=UserReportOut,
    status_code=status.HTTP_201_CREATED,
)
async def report_user(
    user_id: int,
    payload: UserReportCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    target_user = await repo.get_user_by_id(session=session, user_id=user_id)

    if target_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Нельзя пожаловаться на собственный профиль",
        )

    already_reported = await repo.has_reported(
        session=session,
        reporter_id=current_user.id,
        reported_user_id=target_user.id,
    )

    if already_reported:
        raise HTTPException(
            status_code=400,
            detail="Вы уже отправляли жалобу на этого пользователя",
        )

    report = await repo.create_report(
        session=session,
        reporter_id=current_user.id,
        reported_user_id=target_user.id,
        reason=payload.reason,
        comment=payload.comment,
    )

    return UserReportOut(
        id=report.id,
        reason=report.reason,
        comment=report.comment,
        status=report.status,
        created_at=report.created_at,
    )


@router.get("/{user_id}/collections/", response_model=list[CollectionOut])
async def get_user_profile_collections(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User | None = Depends(get_optional_user),
):
    target_user = await repo.get_user_by_id(session=session, user_id=user_id)

    if target_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if target_user.is_profile_blocked and not (
        current_user and (current_user.id == target_user.id or current_user.is_admin)
    ):
        return []

    rows = await collections_repo.get_user_collections(
        session=session,
        user_id=user_id,
    )

    return [
        CollectionOut(
            id=collection.id,
            name=collection.name,
            description=collection.description,
            recipes_count=recipes_count,
            created_at=collection.created_at,
        )
        for collection, recipes_count in rows
    ]


@router.get("/{user_id}/comments/", response_model=list[ProfileCommentOut])
async def get_user_profile_comments(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User | None = Depends(get_optional_user),
):
    target_user = await repo.get_user_by_id(session=session, user_id=user_id)

    if target_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if target_user.is_profile_blocked and not (
        current_user and (current_user.id == target_user.id or current_user.is_admin)
    ):
        return []

    rows = await comments_repo.list_by_user(
        session=session,
        user_id=user_id,
        current_user_id=current_user.id if current_user else None,
    )

    return [ProfileCommentOut(**row) for row in rows]