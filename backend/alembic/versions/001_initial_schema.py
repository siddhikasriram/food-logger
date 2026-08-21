"""Initial schema for users, ingredients, recipes, and meal logs.

Revision ID: 001_initial
Revises:
Create Date: 2026-08-20

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("height_cm", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("weight_kg", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("protein_goal_g", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("calorie_goal", sa.Numeric(precision=7, scale=2), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "ingredients",
        sa.Column("ingredient_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("calories_per_100g", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("protein_per_100g", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("carbs_per_100g", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("fat_per_100g", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column(
            "fiber_per_100g",
            sa.Numeric(precision=8, scale=2),
            nullable=False,
            server_default="0",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("ingredient_id"),
    )
    op.create_index(op.f("ix_ingredients_name"), "ingredients", ["name"], unique=True)

    op.create_table(
        "recipe_tags",
        sa.Column("tag_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("tag_id"),
    )
    op.create_index(op.f("ix_recipe_tags_name"), "recipe_tags", ["name"], unique=True)

    op.create_table(
        "recipes",
        sa.Column("recipe_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column(
            "servings",
            sa.Numeric(precision=6, scale=2),
            nullable=False,
            server_default="1",
        ),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.user_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("recipe_id"),
    )
    op.create_index(op.f("ix_recipes_name"), "recipes", ["name"], unique=False)
    op.create_index(op.f("ix_recipes_created_by"), "recipes", ["created_by"], unique=False)

    op.create_table(
        "recipe_ingredients",
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column("quantity_g", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.ingredient_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.recipe_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("recipe_id", "ingredient_id"),
        sa.UniqueConstraint("recipe_id", "ingredient_id", name="uq_recipe_ingredient"),
    )

    op.create_table(
        "recipe_tag_mapping",
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.recipe_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["recipe_tags.tag_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("recipe_id", "tag_id"),
    )

    op.create_table(
        "meal_logs",
        sa.Column("meal_log_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.Column("meal_type", sa.String(length=20), nullable=False),
        sa.Column("servings", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.recipe_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("meal_log_id"),
    )
    op.create_index(op.f("ix_meal_logs_user_id"), "meal_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_meal_logs_recipe_id"), "meal_logs", ["recipe_id"], unique=False)
    op.create_index(op.f("ix_meal_logs_consumed_at"), "meal_logs", ["consumed_at"], unique=False)
    op.create_index(
        "ix_meal_logs_user_consumed_at",
        "meal_logs",
        ["user_id", "consumed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_meal_logs_user_consumed_at", table_name="meal_logs")
    op.drop_index(op.f("ix_meal_logs_consumed_at"), table_name="meal_logs")
    op.drop_index(op.f("ix_meal_logs_recipe_id"), table_name="meal_logs")
    op.drop_index(op.f("ix_meal_logs_user_id"), table_name="meal_logs")
    op.drop_table("meal_logs")
    op.drop_table("recipe_tag_mapping")
    op.drop_table("recipe_ingredients")
    op.drop_index(op.f("ix_recipes_created_by"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_name"), table_name="recipes")
    op.drop_table("recipes")
    op.drop_index(op.f("ix_recipe_tags_name"), table_name="recipe_tags")
    op.drop_table("recipe_tags")
    op.drop_index(op.f("ix_ingredients_name"), table_name="ingredients")
    op.drop_table("ingredients")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
