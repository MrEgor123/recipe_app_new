"""add recipe_steps

Revision ID: c7ce23f6a18d
Revises: eee292fdce0c
Create Date: 2026-02-13 14:19:27.607762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c7ce23f6a18d"
down_revision = "eee292fdce0c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipe_steps",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "recipe_id",
            sa.Integer(),
            sa.ForeignKey("recipes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("duration_sec", sa.Integer(), nullable=True),
    )

    op.create_index(
        "ix_recipe_steps_recipe_id",
        "recipe_steps",
        ["recipe_id"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_recipe_steps_recipe_id_position",
        "recipe_steps",
        ["recipe_id", "position"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_recipe_steps_recipe_id_position",
        "recipe_steps",
        type_="unique",
    )
    op.drop_index("ix_recipe_steps_recipe_id", table_name="recipe_steps")
    op.drop_table("recipe_steps")