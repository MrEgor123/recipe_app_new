from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RecipeRating(Base):
    __tablename__ = "recipe_ratings"

    __table_args__ = (
        UniqueConstraint("recipe_id", "user_id", name="uq_recipe_ratings_recipe_user"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_recipe_ratings_rating_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)