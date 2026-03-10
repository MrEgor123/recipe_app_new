from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base  # <-- ВАЖНО: один Base на все модели


class RecipeStep(Base):
    __tablename__ = "recipe_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # можно так, чтобы индекс был на колонке
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("recipe_id", "position", name="uq_recipe_steps_recipe_id_position"),
        # этот индекс можно оставить (он полезен), но тогда НЕ дублируй index=True выше
        # Index("ix_recipe_steps_recipe_id_position", "recipe_id", "position"),
    )