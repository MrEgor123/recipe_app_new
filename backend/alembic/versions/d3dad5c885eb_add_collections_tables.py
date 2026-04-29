"""add collections tables

Revision ID: add_collections_tables
Revises: cd0a61664fab
Create Date: 2026-04-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_collections_tables"
down_revision: Union[str, None] = "cd0a61664fab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "collections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_collections_user_name"),
    )
    op.create_index(op.f("ix_collections_user_id"), "collections", ["user_id"], unique=False)

    op.create_table(
        "collection_recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["collection_id"], ["collections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("collection_id", "recipe_id", name="uq_collection_recipe"),
    )
    op.create_index(op.f("ix_collection_recipes_collection_id"), "collection_recipes", ["collection_id"], unique=False)
    op.create_index(op.f("ix_collection_recipes_recipe_id"), "collection_recipes", ["recipe_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_collection_recipes_recipe_id"), table_name="collection_recipes")
    op.drop_index(op.f("ix_collection_recipes_collection_id"), table_name="collection_recipes")
    op.drop_table("collection_recipes")

    op.drop_index(op.f("ix_collections_user_id"), table_name="collections")
    op.drop_table("collections")