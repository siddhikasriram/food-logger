def test_user_model_table() -> None:
    from app.users.models import User, UserIngredientPreference

    assert User.__tablename__ == "users"
    assert UserIngredientPreference.__tablename__ == "user_ingredient_preferences"
