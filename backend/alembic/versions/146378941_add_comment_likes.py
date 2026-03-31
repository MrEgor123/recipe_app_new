"""add comment likes

Revision ID: add_comment_likes
Revises: 12b588a4c39d
Create Date: 2026-03-31 22:30:00

"""
from alembic import op
import sqlalchemy as sa


revision = "add_comment_likes"
down_revision = "12b588a4c39d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "comment_likes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("comment_id", sa.Integer(), sa.ForeignKey("comments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("comment_id", "user_id", name="uq_comment_likes_comment_user"),
    )
    op.create_index("ix_comment_likes_comment_id", "comment_likes", ["comment_id"])
    op.create_index("ix_comment_likes_user_id", "comment_likes", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_comment_likes_user_id", table_name="comment_likes")
    op.drop_index("ix_comment_likes_comment_id", table_name="comment_likes")
    op.drop_table("comment_likes")