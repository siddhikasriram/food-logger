from fastapi.testclient import TestClient


def test_create_recipe_includes_nested_ingredients(client: TestClient) -> None:
    ingredient = client.post(
        "/api/v1/ingredients",
        json={
            "name": "Chicken breast",
            "calories_per_100g": 165,
            "protein_per_100g": 31,
            "carbs_per_100g": 0,
            "fat_per_100g": 3.6,
        },
    )
    assert ingredient.status_code == 201
    ingredient_id = ingredient.json()["ingredient_id"]

    created = client.post(
        "/api/v1/recipes",
        json={
            "name": "Grilled chicken",
            "servings": 1,
            "ingredients": [{"ingredient_id": ingredient_id, "quantity_g": 150}],
        },
    )
    assert created.status_code == 201
    recipe_id = created.json()["recipe_id"]

    fetched = client.get(f"/api/v1/recipes/{recipe_id}")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["name"] == "Grilled chicken"
    assert len(body["ingredients"]) == 1
    assert body["ingredients"][0]["name"] == "Chicken breast"
    assert body["ingredients"][0]["quantity_g"] == 150
    assert body["tags"] == []
