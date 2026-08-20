def test_recipe_model_tables() -> None:
    from app.recipes.models import Recipe, RecipeIngredient, RecipeTag, RecipeTagMapping

    assert Recipe.__tablename__ == "recipes"
    assert RecipeIngredient.__tablename__ == "recipe_ingredients"
    assert RecipeTag.__tablename__ == "recipe_tags"
    assert RecipeTagMapping.__tablename__ == "recipe_tag_mapping"
