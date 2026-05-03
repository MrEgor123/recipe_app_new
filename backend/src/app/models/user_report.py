from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserReport(Base):
    __tablename__ = "user_reports"

    __table_args__ = (
        UniqueConstraint(
            "reporter_id",
            "reported_user_id",
            name="uq_user_reports_reporter_reported",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    reporter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    reported_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(String(120), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default="new")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    reporter = relationship(
        "User",
        foreign_keys=[reporter_id],
        back_populates="reports_created",
    )

    reported_user = relationship(
        "User",
        foreign_keys=[reported_user_id],
        back_populates="reports_received",
    )

    def __str__(self) -> str:
        return f"Жалоба #{self.id}: {self.reason}"