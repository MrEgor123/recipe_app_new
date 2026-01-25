"""add is_admin to users

Revision ID: eee292fdce0c
Revises: 0008_foodgram_fields
Create Date: 2026-01-25 09:10:11.538560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eee292fdce0c'
down_revision = '0008_foodgram_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT false
    """)

def downgrade() -> None:
    op.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS is_admin
    """)
