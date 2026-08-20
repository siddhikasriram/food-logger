from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.recipes.models import Recipe
from app.shared.enums import MealType
from app.users.models import User


class MealLog(Base):
    """A user eating a global recipe. Nutrition is calculated, not stored on the log."""

    __tablename__ = "meal_logs"
    __table_args__ = (Index("ix_meal_logs_user_consumed_at", "user_id", "consumed_at"),)

    meal_log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.recipe_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    meal_type: Mapped[MealType] = mapped_column(
        Enum(MealType, native_enum=False, length=20), nullable=False
    )
    servings: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    consumed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    user: Mapped[User] = relationship()
    recipe: Mapped[Recipe] = relationship()
