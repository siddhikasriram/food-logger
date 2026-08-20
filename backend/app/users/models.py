from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.shared.enums import IngredientPreference

if TYPE_CHECKING:
    from app.ingredients.models import Ingredient


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    height_cm: Mapped[float | None] = mapped_column(Numeric(5, 2))
    weight_kg: Mapped[float | None] = mapped_column(Numeric(5, 2))
    protein_goal_g: Mapped[float | None] = mapped_column(Numeric(6, 2))
    calorie_goal: Mapped[float | None] = mapped_column(Numeric(7, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    ingredient_preferences: Mapped[list["UserIngredientPreference"]] = relationship(
        back_populates="user"
    )


class UserIngredientPreference(Base):
    """User-specific like/dislike of a global ingredient. Not stored as columns on users."""

    __tablename__ = "user_ingredient_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", "ingredient_id", name="uq_user_ingredient_preference"),
    )

    user_ingredient_preference_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.ingredient_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    preference: Mapped[IngredientPreference] = mapped_column(
        Enum(IngredientPreference, native_enum=False, length=20), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="ingredient_preferences")
    ingredient: Mapped["Ingredient"] = relationship()
