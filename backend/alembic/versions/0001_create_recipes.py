"""create recipes table

Revision ID: 0001_create_recipes
Revises: 
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa

revision = "0001_create_recipes"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("cooking_time_minutes", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("recipes")
