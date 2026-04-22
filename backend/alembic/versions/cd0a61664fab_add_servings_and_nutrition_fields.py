from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cd0a61664fab"
down_revision = "20260409_add_recipe_ratings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column("base_servings", sa.Integer(), nullable=False, server_default="1"),
    )

    op.add_column(
        "ingredients",
        sa.Column("calories_per_100g", sa.Numeric(8, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "ingredients",
        sa.Column("protein_per_100g", sa.Numeric(8, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "ingredients",
        sa.Column("fat_per_100g", sa.Numeric(8, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "ingredients",
        sa.Column("carbs_per_100g", sa.Numeric(8, 2), nullable=False, server_default="0"),
    )

    op.alter_column("recipes", "base_servings", server_default=None)
    op.alter_column("ingredients", "calories_per_100g", server_default=None)
    op.alter_column("ingredients", "protein_per_100g", server_default=None)
    op.alter_column("ingredients", "fat_per_100g", server_default=None)
    op.alter_column("ingredients", "carbs_per_100g", server_default=None)


def downgrade() -> None:
    op.drop_column("ingredients", "carbs_per_100g")
    op.drop_column("ingredients", "fat_per_100g")
    op.drop_column("ingredients", "protein_per_100g")
    op.drop_column("ingredients", "calories_per_100g")
    op.drop_column("recipes", "base_servings")