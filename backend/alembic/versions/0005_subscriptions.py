"""subscriptions

Revision ID: 0005_subscriptions
Revises: 0004_favorites
Create Date: 2026-01-19

"""
from alembic import op
import sqlalchemy as sa

revision = "0005_subscriptions"
down_revision = "0004_favorites"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("user_id", "author_id", name="uq_subscriptions_user_author"),
    )


def downgrade() -> None:
    op.drop_table("subscriptions")