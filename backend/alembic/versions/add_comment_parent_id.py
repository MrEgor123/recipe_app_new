"""add parent_id to comments

Revision ID: add_comment_parent_id
Revises: add_comment_likes
Create Date: 2026-03-31 23:00:00

"""
from alembic import op
import sqlalchemy as sa


revision = "add_comment_parent_id"
down_revision = "add_comment_likes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("comments", sa.Column("parent_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "comments_parent_id_fkey",
        "comments",
        "comments",
        ["parent_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_comments_parent_id", "comments", ["parent_id"])


def downgrade() -> None:
    op.drop_index("ix_comments_parent_id", table_name="comments")
    op.drop_constraint("comments_parent_id_fkey", "comments", type_="foreignkey")
    op.drop_column("comments", "parent_id")