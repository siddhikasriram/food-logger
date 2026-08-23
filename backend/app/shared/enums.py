from enum import StrEnum


class MealType(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class QuantityUnit(StrEnum):
    """MVP stores quantities in grams; other units can be added later."""

    GRAMS = "g"


class NutritionSource(StrEnum):
    MANUAL = "manual"
    LLM_ESTIMATE = "llm_estimate"


class OntologyScope(StrEnum):
    ALL = "all"
    LOGGING = "logging"
