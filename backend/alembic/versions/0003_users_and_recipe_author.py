"""users and recipe author

Revision ID: 0003_users_and_recipe_author
Revises: 0002_tags_ingredients_links
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa

revision = "0003_users_and_recipe_author"
down_revision = "0002_tags_ingredients_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("username", sa.String(length=60), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    # добавляем author_id в recipes
    op.add_column("recipes", sa.Column("author_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_recipes_author_id_users",
        "recipes",
        "users",
        ["author_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # создаём "технического" пользователя для старых рецептов, если они уже есть
    op.execute(
        sa.text(
            "INSERT INTO users (email, username, password_hash, is_admin) "
            "VALUES ('system@local', 'system', '!', true) "
            "ON CONFLICT DO NOTHING"
        )
    )
    op.execute(sa.text("UPDATE recipes SET author_id = (SELECT id FROM users WHERE username='system') WHERE author_id IS NULL"))

    op.alter_column("recipes", "author_id", nullable=False)


def downgrade() -> None:
    op.drop_constraint("fk_recipes_author_id_users", "recipes", type_="foreignkey")
    op.drop_column("recipes", "author_id")
    op.drop_table("users")