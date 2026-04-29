from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.comment_like import CommentLike
from app.models.recipe import Recipe
from app.models.user import User


class CommentRepository:
    async def list_by_recipe(
        self,
        session: AsyncSession,
        recipe_id: int,
        current_user_id: int | None = None,
    ) -> list[dict]:
        likes_subq = (
            select(
                CommentLike.comment_id.label("comment_id"),
                func.count(CommentLike.id).label("likes_count"),
            )
            .group_by(CommentLike.comment_id)
            .subquery()
        )

        stmt = (
            select(
                Comment,
                func.coalesce(likes_subq.c.likes_count, 0).label("likes_count"),
            )
            .outerjoin(likes_subq, likes_subq.c.comment_id == Comment.id)
            .where(Comment.recipe_id == recipe_id)
            .order_by(
                Comment.parent_id.asc().nullsfirst(),
                func.coalesce(likes_subq.c.likes_count, 0).desc(),
                Comment.created_at.desc(),
                Comment.id.desc(),
            )
        )

        rows = (await session.execute(stmt)).all()

        liked_ids: set[int] = set()
        if current_user_id is not None and rows:
            comment_ids = [row[0].id for row in rows]
            liked_stmt = select(CommentLike.comment_id).where(
                CommentLike.user_id == current_user_id,
                CommentLike.comment_id.in_(comment_ids),
            )
            liked_ids = set((await session.execute(liked_stmt)).scalars().all())

        result = []
        for comment, likes_count in rows:
            result.append(
                {
                    "comment": comment,
                    "likes_count": int(likes_count or 0),
                    "is_liked": comment.id in liked_ids,
                }
            )
        return result

    async def list_by_user(
        self,
        session: AsyncSession,
        user_id: int,
        current_user_id: int | None = None,
    ) -> list[dict]:
        likes_subq = (
            select(
                CommentLike.comment_id.label("comment_id"),
                func.count(CommentLike.id).label("likes_count"),
            )
            .group_by(CommentLike.comment_id)
            .subquery()
        )

        stmt = (
            select(
                Comment,
                User,
                Recipe,
                func.coalesce(likes_subq.c.likes_count, 0).label("likes_count"),
            )
            .join(User, User.id == Comment.author_id)
            .join(Recipe, Recipe.id == Comment.recipe_id)
            .outerjoin(likes_subq, likes_subq.c.comment_id == Comment.id)
            .where(Comment.author_id == user_id)
            .order_by(Comment.created_at.desc(), Comment.id.desc())
        )

        rows = (await session.execute(stmt)).all()

        liked_ids: set[int] = set()
        if current_user_id is not None and rows:
            comment_ids = [comment.id for comment, _, _, _ in rows]
            liked_stmt = select(CommentLike.comment_id).where(
                CommentLike.user_id == current_user_id,
                CommentLike.comment_id.in_(comment_ids),
            )
            liked_ids = set((await session.execute(liked_stmt)).scalars().all())

        result: list[dict] = []
        for comment, author, recipe, likes_count in rows:
            recipe_title = getattr(recipe, "title", None) or getattr(recipe, "name", None)

            result.append(
                {
                    "id": comment.id,
                    "text": comment.text,
                    "created_at": comment.created_at,
                    "parent_id": comment.parent_id,
                    "likes_count": int(likes_count or 0),
                    "is_liked": comment.id in liked_ids,
                    "author": {
                        "id": author.id,
                        "username": author.username,
                        "first_name": author.first_name,
                        "last_name": author.last_name,
                        "avatar": author.avatar,
                    },
                    "recipe": {
                        "id": recipe.id,
                        "title": recipe_title,
                        "image": getattr(recipe, "image", None),
                    },
                }
            )

        return result

    async def get(self, session: AsyncSession, comment_id: int) -> Comment | None:
        stmt = select(Comment).where(Comment.id == comment_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def create(
        self,
        session: AsyncSession,
        recipe_id: int,
        author_id: int,
        text: str,
        parent_id: int | None = None,
    ) -> Comment:
        comment = Comment(
            recipe_id=recipe_id,
            author_id=author_id,
            parent_id=parent_id,
            text=text.strip(),
        )
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment

    async def update(self, session: AsyncSession, comment: Comment, text: str) -> Comment:
        comment.text = text.strip()
        await session.commit()
        await session.refresh(comment)
        return comment

    async def delete(self, session: AsyncSession, comment: Comment) -> None:
        await session.delete(comment)
        await session.commit()

    async def get_likes_count(self, session: AsyncSession, comment_id: int) -> int:
        stmt = select(func.count(CommentLike.id)).where(CommentLike.comment_id == comment_id)
        result = await session.execute(stmt)
        return int(result.scalar() or 0)

    async def is_liked_by_user(
        self,
        session: AsyncSession,
        comment_id: int,
        user_id: int,
    ) -> bool:
        stmt = select(CommentLike.id).where(
            CommentLike.comment_id == comment_id,
            CommentLike.user_id == user_id,
        )
        result = await session.execute(stmt)
        return result.scalar() is not None

    async def add_like(
        self,
        session: AsyncSession,
        comment_id: int,
        user_id: int,
    ) -> None:
        exists_stmt = select(CommentLike.id).where(
            CommentLike.comment_id == comment_id,
            CommentLike.user_id == user_id,
        )
        exists = await session.execute(exists_stmt)
        if exists.scalar() is None:
            session.add(CommentLike(comment_id=comment_id, user_id=user_id))
            await session.commit()

    async def remove_like(
        self,
        session: AsyncSession,
        comment_id: int,
        user_id: int,
    ) -> None:
        stmt = select(CommentLike).where(
            CommentLike.comment_id == comment_id,
            CommentLike.user_id == user_id,
        )
        like = (await session.execute(stmt)).scalars().first()
        if like is not None:
            await session.delete(like)
            await session.commit()

    async def delete_by_recipe(self, session: AsyncSession, recipe_id: int) -> None:
        stmt = delete(Comment).where(Comment.recipe_id == recipe_id)
        await session.execute(stmt)
        await session.commit()