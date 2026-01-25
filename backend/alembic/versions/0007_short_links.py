"""short links

Revision ID: 0007_short_links
Revises: 0006_shopping_cart
Create Date: 2026-01-19

"""
from alembic import op
import sqlalchemy as sa

revision = "0007_short_links"
down_revision = "0006_shopping_cart"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "short_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.UniqueConstraint("code", name="uq_short_links_code"),
    )


def downgrade() -> None:
    op.drop_table("short_links")