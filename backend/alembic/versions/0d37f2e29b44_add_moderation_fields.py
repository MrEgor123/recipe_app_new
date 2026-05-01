"""add moderation fields

Revision ID: 0d37f2e29b44
Revises: 8f3f3f1f0a21
Create Date: 2026-05-01 11:41:23.227266

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d37f2e29b44'
down_revision = '8f3f3f1f0a21'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'recipes',
        sa.Column(
            'moderation_status',
            sa.String(length=20),
            nullable=False,
            server_default='pending'
        )
    )
    op.add_column(
        'recipes',
        sa.Column(
            'is_published',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )


def downgrade() -> None:
    op.drop_column('recipes', 'is_published')
    op.drop_column('recipes', 'moderation_status')