from decimal import Decimal

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)

    calories_per_100g: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=0)
    protein_per_100g: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=0)
    fat_per_100g: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=0)
    carbs_per_100g: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=0)