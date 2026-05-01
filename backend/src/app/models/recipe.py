from sqlalchemy import ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[str | None] = mapped_column(Text, nullable=True)

    cooking_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    base_servings: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    moderation_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending"
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    author = relationship("User")
    comments = relationship(
        "Comment",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __str__(self) -> str:
        return self.title