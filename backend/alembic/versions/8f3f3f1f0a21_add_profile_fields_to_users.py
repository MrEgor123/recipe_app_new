"""add profile fields to users

Revision ID: 8f3f3f1f0a21
Revises: add_collections_tables
Create Date: 2026-04-25 16:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "8f3f3f1f0a21"
down_revision = "add_collections_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("status", sa.String(length=120), nullable=True))
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("cover_image", sa.Text(), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "created_at")
    op.drop_column("users", "cover_image")
    op.drop_column("users", "bio")
    op.drop_column("users", "status")