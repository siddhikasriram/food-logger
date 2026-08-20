def test_meal_log_model_table() -> None:
    from app.meals.models import MealLog

    assert MealLog.__tablename__ == "meal_logs"
