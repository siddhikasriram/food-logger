def test_ingredient_model_table() -> None:
    from app.ingredients.models import Ingredient

    assert Ingredient.__tablename__ == "ingredients"
