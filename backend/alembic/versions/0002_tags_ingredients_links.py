"""tags, ingredients, and recipe links

Revision ID: 0002_tags_ingredients_links
Revises: 0001_create_recipes
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa

revision = "0002_tags_ingredients_links"
down_revision = "0001_create_recipes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=60), nullable=False, unique=True),
        sa.Column("slug", sa.String(length=60), nullable=False, unique=True),
        sa.Column("color", sa.String(length=7), nullable=False),
    )

    op.create_table(
        "ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("unit", sa.String(length=32), nullable=False),
    )

    op.create_table(
        "recipe_tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("recipe_id", "tag_id", name="uq_recipe_tag"),
    )

    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.UniqueConstraint("recipe_id", "ingredient_id", name="uq_recipe_ingredient"),
    )


def downgrade() -> None:
    op.drop_table("recipe_ingredients")
    op.drop_table("recipe_tags")
    op.drop_table("ingredients")
    op.drop_table("tags")