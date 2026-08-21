from datetime import datetime

from fastapi.testclient import TestClient


def test_daily_protein_from_logged_meal(client: TestClient) -> None:
    user = client.post(
        "/api/v1/users",
        json={
            "name": "Ada",
            "email": "ada@example.com",
            "protein_goal_g": 50,
        },
    ).json()
    ingredient = client.post(
        "/api/v1/ingredients",
        json={
            "name": "Chicken",
            "calories_per_100g": 165,
            "protein_per_100g": 20,
            "carbs_per_100g": 0,
            "fat_per_100g": 3.6,
        },
    ).json()
    recipe = client.post(
        "/api/v1/recipes",
        json={
            "name": "Chicken bowl",
            "ingredients": [{"ingredient_id": ingredient["ingredient_id"], "quantity_g": 100}],
        },
    ).json()

    consumed_at = datetime(2026, 8, 20, 12, 0).isoformat()
    logged = client.post(
        "/api/v1/meals",
        json={
            "user_id": user["user_id"],
            "recipe_id": recipe["recipe_id"],
            "meal_type": "lunch",
            "servings": 2,
            "consumed_at": consumed_at,
        },
    )
    assert logged.status_code == 201
    assert logged.json()["recipe_name"] == "Chicken bowl"

    summary = client.get(
        f"/api/v1/nutrition/users/{user['user_id']}/daily",
        params={"day": "2026-08-20"},
    )
    assert summary.status_code == 200
    body = summary.json()
    assert body["protein_goal_g"] == 50
    assert body["protein_consumed_g"] == 40
    assert body["protein_remaining_g"] == 10
    assert body["progress_percent"] == 80
