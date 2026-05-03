"""add moderation rejections count

Revision ID: 1b7c8d9e0f11
Revises: 0d37f2e29b44
Create Date: 2026-05-03 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "1b7c8d9e0f11"
down_revision = "0d37f2e29b44"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "moderation_rejections_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "moderation_rejections_count")