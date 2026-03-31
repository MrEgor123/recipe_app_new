from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.deps import get_current_user_token, get_optional_user_token
from app.models.user import User
from app.repositories.comments import CommentRepository
from app.repositories.recipes import RecipeRepository
from app.repositories.users import UserRepository
from app.schemas.comments import (
    CommentCreate,
    CommentUpdate,
    CommentOut,
    CommentAuthorOut,
)

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
        raise HTTPException(status_code=500, detail="Comment author not found")

    if likes_count is None:
        likes_count = await comments_repo.get_likes_count(session, comment.id)

    if is_liked is None:
        is_liked = False
        if current_user_id is not None:
            is_liked = await comments_repo.is_liked_by_user(session, comment.id, current_user_id)

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


@router.get("/recipes/{recipe_id}/comments/", response_model=list[CommentOut])
async def list_recipe_comments(
    recipe_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_optional_user_token),
):
    recipe = await recipes_repo.get(session, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

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
        raise HTTPException(status_code=404, detail="Recipe not found")

    if payload.parent_id is not None:
        parent = await comments_repo.get(session, payload.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if parent.recipe_id != recipe_id:
            raise HTTPException(status_code=400, detail="Parent comment belongs to another recipe")

    comment = await comments_repo.create(
        session=session,
        recipe_id=recipe_id,
        author_id=user.id,
        text=payload.text,
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
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")

    comment = await comments_repo.update(session, comment, payload.text)
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
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")

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
        raise HTTPException(status_code=404, detail="Comment not found")

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
        raise HTTPException(status_code=404, detail="Comment not found")

    await comments_repo.remove_like(session, comment_id=comment_id, user_id=user.id)

    likes_count = await comments_repo.get_likes_count(session, comment_id)
    return await _comment_to_out(
        session=session,
        comment=comment,
        current_user_id=user.id,
        likes_count=likes_count,
        is_liked=False,
    )