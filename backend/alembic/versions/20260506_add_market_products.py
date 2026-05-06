"""add market products

Revision ID: 20260506_market_products
Revises: 2c8d9e0f1122
Create Date: 2026-05-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260506_market_products"
down_revision: Union[str, None] = "2c8d9e0f1122"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "market_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column("market_id", sa.String(length=50), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("product_url", sa.String(length=1000), nullable=True),
        sa.Column("package_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("package_unit", sa.String(length=50), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(
            ["ingredient_id"],
            ["ingredients.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_market_products_ingredient_id",
        "market_products",
        ["ingredient_id"],
        unique=False,
    )

    op.create_index(
        "ix_market_products_market_id",
        "market_products",
        ["market_id"],
        unique=False,
    )

    op.create_index(
        "ix_market_products_ingredient_market",
        "market_products",
        ["ingredient_id", "market_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_market_products_ingredient_market", table_name="market_products")
    op.drop_index("ix_market_products_market_id", table_name="market_products")
    op.drop_index("ix_market_products_ingredient_id", table_name="market_products")
    op.drop_table("market_products")