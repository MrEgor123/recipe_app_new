from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.deps import get_current_user_token, get_optional_user_token
from app.models.user import User
from app.repositories.comments import CommentRepository
from app.repositories.recipes import RecipeRepository
from app.repositories.users import UserRepository
from app.schemas.comments import (
    CommentAuthorOut,
    CommentCreate,
    CommentOut,
    CommentUpdate,
)
from app.utils.moderation import moderate_comment_full

router = APIRouter(prefix="/api", tags=["comments"])

comments_repo = CommentRepository()
recipes_repo = RecipeRepository()
users_repo = UserRepository()


def _author_to_out(user: User) -> CommentAuthorOut:
    return CommentAuthorOut(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        avatar=user.avatar,
    )


async def _comment_to_out(
    session: AsyncSession,
    comment,
    current_user_id: int | None = None,
    likes_count: int | None = None,
    is_liked: bool | None = None,
    replies: list[CommentOut] | None = None,
) -> CommentOut:
    author = await users_repo.get_by_id(session, comment.author_id)
    if author is None:
        raise HTTPException(status_code=500, detail="Автор комментария не найден")

    if likes_count is None:
        likes_count = await comments_repo.get_likes_count(session, comment.id)

    if is_liked is None:
        is_liked = False
        if current_user_id is not None:
            is_liked = await comments_repo.is_liked_by_user(
                session,
                comment.id,
                current_user_id,
            )

    return CommentOut(
        id=comment.id,
        text=comment.text,
        created_at=comment.created_at,
        parent_id=comment.parent_id,
        likes_count=likes_count,
        is_liked=is_liked,
        author=_author_to_out(author),
        replies=replies or [],
    )


async def _validate_comment_text(
    *,
    session: AsyncSession,
    recipe_id: int,
    author_id: int,
    text: str,
    parent_id: int | None = None,
    check_spam: bool = True,
) -> str:
    clean_text = (text or "").strip()

    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Комментарий не может быть пустым",
        )

    if len(clean_text) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Комментарий должен быть не длиннее 2000 символов",
        )

    moderation_status = await moderate_comment_full(clean_text)
    if moderation_status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Комментарий не прошёл модерацию. "
                "Запрещены спам, бессмысленный текст, опасные темы и оскорбительное содержание."
            ),
        )

    if check_spam:
        recent_count = await comments_repo.count_recent_comments_by_user(
            session,
            author_id=author_id,
            seconds=15,
        )
        if recent_count >= 1:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Не отправляйте комментарии слишком часто. Подождите несколько секунд.",
            )

        has_duplicate = await comments_repo.has_duplicate_recent_comment(
            session,
            recipe_id=recipe_id,
            author_id=author_id,
            text_value=clean_text,
            parent_id=parent_id,
        )
        if has_duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Такой комментарий уже был отправлен.",
            )

    return clean_text


@router.get("/recipes/{recipe_id}/comments/", response_model=list[CommentOut])
async def list_recipe_comments(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_optional_user_token),
):
    recipe = await recipes_repo.get(session, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    current_user_id = current_user.id if current_user else None
    rows = await comments_repo.list_by_recipe(
        session=session,
        recipe_id=recipe_id,
        current_user_id=current_user_id,
    )

    comments_map: dict[int, CommentOut] = {}
    root_comments: list[CommentOut] = []

    for row in rows:
        out = await _comment_to_out(
            session=session,
            comment=row["comment"],
            current_user_id=current_user_id,
            likes_count=row["likes_count"],
            is_liked=row["is_liked"],
        )
        comments_map[out.id] = out

    for row in rows:
        comment = row["comment"]
        out = comments_map[comment.id]
        if comment.parent_id is None:
            root_comments.append(out)
        else:
            parent = comments_map.get(comment.parent_id)
            if parent:
                parent.replies.append(out)

    return root_comments


@router.post(
    "/recipes/{recipe_id}/comments/",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe_comment(
    recipe_id: int,
    payload: CommentCreate,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    recipe = await recipes_repo.get(session, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")

    if getattr(user, "is_blocked", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Заблокированный пользователь не может оставлять комментарии.",
        )

    if payload.parent_id is not None:
        parent = await comments_repo.get(session, payload.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Родительский комментарий не найден")
        if parent.recipe_id != recipe_id:
            raise HTTPException(
                status_code=400,
                detail="Родительский комментарий относится к другому рецепту",
            )

    clean_text = await _validate_comment_text(
        session=session,
        recipe_id=recipe_id,
        author_id=user.id,
        text=payload.text,
        parent_id=payload.parent_id,
        check_spam=True,
    )

    comment = await comments_repo.create(
        session=session,
        recipe_id=recipe_id,
        author_id=user.id,
        text=clean_text,
        parent_id=payload.parent_id,
    )
    return await _comment_to_out(
        session=session,
        comment=comment,
        current_user_id=user.id,
        likes_count=0,
        is_liked=False,
    )


@router.patch("/comments/{comment_id}/", response_model=CommentOut)
async def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    comment = await comments_repo.get(session, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    if comment.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    if getattr(user, "is_blocked", False) and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Заблокированный пользователь не может редактировать комментарии.",
        )

    clean_text = await _validate_comment_text(
        session=session,
        recipe_id=comment.recipe_id,
        author_id=user.id,
        text=payload.text,
        parent_id=comment.parent_id,
        check_spam=False,
    )

    comment = await comments_repo.update(session, comment, clean_text)
    return await _comment_to_out(
        session=session,
        comment=comment,
        current_user_id=user.id,
    )


@router.delete("/comments/{comment_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    comment = await comments_repo.get(session, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    if comment.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    await comments_repo.delete(session, comment)
    return None


@router.post("/comments/{comment_id}/like/", response_model=CommentOut)
async def like_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    comment = await comments_repo.get(session, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    await comments_repo.add_like(session, comment_id=comment_id, user_id=user.id)

    likes_count = await comments_repo.get_likes_count(session, comment_id)
    return await _comment_to_out(
        session=session,
        comment=comment,
        current_user_id=user.id,
        likes_count=likes_count,
        is_liked=True,
    )


@router.delete("/comments/{comment_id}/like/", status_code=status.HTTP_200_OK)
async def unlike_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(get_current_user_token),
):
    comment = await comments_repo.get(session, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    await comments_repo.remove_like(session, comment_id=comment_id, user_id=user.id)

    likes_count = await comments_repo.get_likes_count(session, comment_id)
    return await _comment_to_out(
        session=session,
        comment=comment,
        current_user_id=user.id,
        likes_count=likes_count,
        is_liked=False,
    )