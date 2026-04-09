from alembic import op
import sqlalchemy as sa


revision = "20260409_add_recipe_ratings"
down_revision = "add_comment_parent_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipe_ratings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("recipe_id", "user_id", name="uq_recipe_ratings_recipe_user"),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_recipe_ratings_rating_range"),
    )


def downgrade() -> None:
    op.drop_table("recipe_ratings")