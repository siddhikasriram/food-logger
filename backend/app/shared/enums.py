from enum import StrEnum


class MealType(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class IngredientPreference(StrEnum):
    LIKED = "liked"
    DISLIKED = "disliked"


class QuantityUnit(StrEnum):
    """MVP stores quantities in grams; other units can be added later."""

    GRAMS = "g"
