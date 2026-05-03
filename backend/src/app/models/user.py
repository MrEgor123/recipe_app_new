from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)

    first_name: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(150), nullable=False, default="")

    avatar: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(120), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        default=False,
    )

    is_blocked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        default=False,
    )
    blocked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    block_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    moderation_rejections_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        default=0,
    )

    comments = relationship(
        "Comment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reports_received = relationship(
        "UserReport",
        foreign_keys="UserReport.reported_user_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reports_created = relationship(
        "UserReport",
        foreign_keys="UserReport.reporter_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def is_profile_blocked(self) -> bool:
        if not self.is_blocked:
            return False

        if self.blocked_until is None:
            return True

        return self.blocked_until > datetime.now(self.blocked_until.tzinfo)

    def __str__(self) -> str:
        full_name = f"{self.first_name} {self.last_name}".strip()

        if full_name:
            return f"{full_name} ({self.username})"

        return self.username