"""merge user reports and moderation counter heads

Revision ID: 2c8d9e0f1122
Revises: 1b7c8d9e0f11, 20260503_user_reports
Create Date: 2026-05-03 16:30:00.000000

"""
from alembic import op


revision = "2c8d9e0f1122"
down_revision = ("1b7c8d9e0f11", "20260503_user_reports")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass