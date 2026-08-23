from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.model.ingredient import Ingredient
    from app.model.user import User


class Recipe(Base):
    """Globally reusable recipe. created_by is attribution, not exclusive ownership."""

    __tablename__ = "recipes"

    recipe_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    instructions: Mapped[str | None] = mapped_column(Text)
    servings: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=1)
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    creator: Mapped["User | None"] = relationship()
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    tag_mappings: Mapped[list["RecipeTagMapping"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )


class RecipeIngredient(Base):
    """Junction: a recipe uses a global ingredient at a quantity in grams (MVP)."""

    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        UniqueConstraint("recipe_id", "ingredient_id", name="uq_recipe_ingredient"),
    )

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.recipe_id", ondelete="CASCADE"), primary_key=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.ingredient_id", ondelete="RESTRICT"), primary_key=True
    )
    quantity_g: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)

    recipe: Mapped[Recipe] = relationship(back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship()


class RecipeTag(Base):
    __tablename__ = "recipe_tags"

    tag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    mappings: Mapped[list["RecipeTagMapping"]] = relationship(back_populates="tag")


class RecipeTagMapping(Base):
    """Normalized many-to-many: recipes <-> recipe_tags. Do not store tags as a string."""

    __tablename__ = "recipe_tag_mapping"

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.recipe_id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("recipe_tags.tag_id", ondelete="CASCADE"), primary_key=True
    )

    recipe: Mapped[Recipe] = relationship(back_populates="tag_mappings")
    tag: Mapped[RecipeTag] = relationship(back_populates="mappings")
