from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.models.comment import Comment
from app.models.favorite import Favorite
from app.models.recipe import Recipe
from app.models.recipe_rating import RecipeRating
from app.models.subscription import Subscription
from app.models.user import User
from app.models.user_report import UserReport


class ProfileRepository:
    async def get_user_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def is_subscribed(
        self,
        session: AsyncSession,
        current_user_id: int,
        target_user_id: int,
    ) -> bool:
        result = await session.execute(
            select(Subscription.id).where(
                Subscription.user_id == current_user_id,
                Subscription.author_id == target_user_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_stats(self, session: AsyncSession, user_id: int) -> dict:
        recipes_count = await session.scalar(
            select(func.count(Recipe.id)).where(
                Recipe.author_id == user_id,
                Recipe.is_published.is_(True),
                Recipe.moderation_status == "approved",
            )
        )

        followers_count = await session.scalar(
            select(func.count(Subscription.id)).where(
                Subscription.author_id == user_id
            )
        )

        following_count = await session.scalar(
            select(func.count(Subscription.id)).where(
                Subscription.user_id == user_id
            )
        )

        comments_count = await session.scalar(
            select(func.count(Comment.id)).where(
                Comment.author_id == user_id
            )
        )

        collections_count = await session.scalar(
            select(func.count(Collection.id)).where(
                Collection.user_id == user_id
            )
        )

        total_recipe_likes = await session.scalar(
            select(func.count(Favorite.id))
            .select_from(Favorite)
            .join(Recipe, Recipe.id == Favorite.recipe_id)
            .where(
                Recipe.author_id == user_id,
                Recipe.is_published.is_(True),
                Recipe.moderation_status == "approved",
            )
        )

        return {
            "recipes_count": recipes_count or 0,
            "followers_count": followers_count or 0,
            "following_count": following_count or 0,
            "comments_count": comments_count or 0,
            "collections_count": collections_count or 0,
            "total_recipe_likes": total_recipe_likes or 0,
        }

    async def get_user_recipes(self, session: AsyncSession, user_id: int) -> list[dict]:
        result = await session.execute(
            select(
                Recipe.id,
                Recipe.title,
                Recipe.image,
                Recipe.cooking_time_minutes,
                func.coalesce(func.avg(RecipeRating.rating), 0).label("rating_avg"),
                func.count(RecipeRating.id).label("rating_count"),
            )
            .outerjoin(RecipeRating, RecipeRating.recipe_id == Recipe.id)
            .where(
                Recipe.author_id == user_id,
                Recipe.is_published.is_(True),
                Recipe.moderation_status == "approved",
            )
            .group_by(
                Recipe.id,
                Recipe.title,
                Recipe.image,
                Recipe.cooking_time_minutes,
            )
            .order_by(Recipe.id.desc())
        )

        rows = result.all()

        return [
            {
                "id": row.id,
                "title": row.title,
                "image": row.image,
                "cooking_time_minutes": row.cooking_time_minutes,
                "rating_avg": float(row.rating_avg or 0),
                "rating_count": int(row.rating_count or 0),
            }
            for row in rows
        ]

    async def create_report(
        self,
        session: AsyncSession,
        reporter_id: int,
        reported_user_id: int,
        reason: str,
        comment: str | None,
    ) -> UserReport:
        report = UserReport(
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            reason=reason,
            comment=comment,
        )

        session.add(report)
        await session.commit()
        await session.refresh(report)

        return report

    async def has_reported(
        self,
        session: AsyncSession,
        reporter_id: int,
        reported_user_id: int,
    ) -> bool:
        result = await session.execute(
            select(UserReport.id).where(
                UserReport.reporter_id == reporter_id,
                UserReport.reported_user_id == reported_user_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def update_profile(
        self,
        session: AsyncSession,
        user: User,
        updates: dict,
    ) -> User:
        for field_name, value in updates.items():
            setattr(user, field_name, value)

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user