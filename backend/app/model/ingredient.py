from datetime import datetime

from sqlalchemy import DateTime, Enum, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.enums import NutritionSource


class Ingredient(Base):
    __tablename__ = "ingredients"

    ingredient_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    calories_per_100g: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    protein_per_100g: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    carbs_per_100g: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    fat_per_100g: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    fiber_per_100g: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, default=0)
    nutrition_source: Mapped[NutritionSource] = mapped_column(
        Enum(
            NutritionSource,
            native_enum=False,
            length=20,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=NutritionSource.MANUAL,
        server_default=NutritionSource.MANUAL.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
