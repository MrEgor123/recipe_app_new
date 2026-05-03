"""add user reports and user blocking

Revision ID: 20260503_user_reports
Revises: 0d37f2e29b44
Create Date: 2026-05-03 15:11:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260503_user_reports"
down_revision: Union[str, None] = "0d37f2e29b44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_blocked",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "users",
        sa.Column("blocked_until", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("block_reason", sa.Text(), nullable=True),
    )

    op.create_table(
        "user_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reporter_id", sa.Integer(), nullable=False),
        sa.Column("reported_user_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=120), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="new"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["reporter_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reported_user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "reporter_id",
            "reported_user_id",
            name="uq_user_reports_reporter_reported",
        ),
    )

    op.create_index(
        "ix_user_reports_reported_user_id",
        "user_reports",
        ["reported_user_id"],
    )
    op.create_index(
        "ix_user_reports_reporter_id",
        "user_reports",
        ["reporter_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_user_reports_reporter_id", table_name="user_reports")
    op.drop_index("ix_user_reports_reported_user_id", table_name="user_reports")
    op.drop_table("user_reports")

    op.drop_column("users", "block_reason")
    op.drop_column("users", "blocked_until")
    op.drop_column("users", "is_blocked")