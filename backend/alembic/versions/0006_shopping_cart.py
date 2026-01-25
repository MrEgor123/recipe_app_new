"""shopping cart

Revision ID: 0006_shopping_cart
Revises: 0005_subscriptions
Create Date: 2026-01-19

"""
from alembic import op
import sqlalchemy as sa

revision = "0006_shopping_cart"
down_revision = "0005_subscriptions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shopping_cart",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("user_id", "recipe_id", name="uq_shopping_cart_user_recipe"),
    )


def downgrade() -> None:
    op.drop_table("shopping_cart")