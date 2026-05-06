from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MarketProduct(Base):
    __tablename__ = "market_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    market_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    package_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    package_unit: Mapped[str] = mapped_column(String(50), nullable=False)

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    ingredient = relationship("Ingredient")