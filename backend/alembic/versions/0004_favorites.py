"""favorites

Revision ID: 0004_favorites
Revises: 0003_users_and_recipe_author
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa

revision = "0004_favorites"
down_revision = "0003_users_and_recipe_author"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("user_id", "recipe_id", name="uq_favorites_user_recipe"),
    )


def downgrade() -> None:
    op.drop_table("favorites")