"""foodgram fields

Revision ID: 0008_foodgram_fields
Revises: 0007_short_links
Create Date: 2026-01-24

"""

from alembic import op
import sqlalchemy as sa


revision = "0008_foodgram_fields"
down_revision = "0007_short_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users: first/last name + avatar
    op.add_column("users", sa.Column("first_name", sa.String(length=150), nullable=False, server_default=""))
    op.add_column("users", sa.Column("last_name", sa.String(length=150), nullable=False, server_default=""))
    op.add_column("users", sa.Column("avatar", sa.Text(), nullable=True))

    # recipes: image (data URL / base64)
    op.add_column("recipes", sa.Column("image", sa.Text(), nullable=True))

    # remove server defaults (keep python defaults)
    op.alter_column("users", "first_name", server_default=None)
    op.alter_column("users", "last_name", server_default=None)


def downgrade() -> None:
    op.drop_column("recipes", "image")
    op.drop_column("users", "avatar")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
