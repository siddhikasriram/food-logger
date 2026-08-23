def test_ingredient_model_table() -> None:
    from app.model.ingredient import Ingredient

    assert Ingredient.__tablename__ == "ingredients"
