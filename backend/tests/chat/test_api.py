from datetime import datetime

from fastapi.testclient import TestClient

from app.chat.router import get_meal_parser
from app.chat.schemas import ParsedIngredient, ParsedMeal
from app.shared.exceptions import ServiceUnavailableError


class FakeParser:
    def __init__(self, result: ParsedMeal) -> None:
        self.result = result
        self.catalog: dict[str, object] | None = None

    def parse(self, _message: str, catalog: dict[str, object]) -> ParsedMeal:
        self.catalog = catalog
        return self.result


class FailingParser:
    def parse(self, _message: str, _catalog: dict[str, object]) -> ParsedMeal:
        raise ServiceUnavailableError("LLM unavailable")


def create_user(client: TestClient) -> dict:
    return client.post(
        "/api/v1/users",
        json={
            "name": "Ada",
            "email": "ada@example.com",
            "protein_goal_g": 100,
        },
    ).json()


def existing_ingredient(
    ingredient_id: int, name: str, quantity_g: float
) -> ParsedIngredient:
    return ParsedIngredient(
        ingredient_id=ingredient_id,
        name=name,
        quantity_g=quantity_g,
        calories_per_100g=None,
        protein_per_100g=None,
        carbs_per_100g=None,
        fat_per_100g=None,
        fiber_per_100g=None,
    )


def test_existing_recipe_requires_confirmation_before_logging(
    client: TestClient,
) -> None:
    user = create_user(client)
    ingredient = client.post(
        "/api/v1/ingredients",
        json={
            "name": "Chicken",
            "calories_per_100g": 165,
            "protein_per_100g": 20,
            "carbs_per_100g": 0,
            "fat_per_100g": 4,
        },
    ).json()
    recipe = client.post(
        "/api/v1/recipes",
        json={
            "name": "Chicken bowl",
            "ingredients": [
                {
                    "ingredient_id": ingredient["ingredient_id"],
                    "quantity_g": 100,
                }
            ],
        },
    ).json()
    parser = FakeParser(
        ParsedMeal(
            recipe_id=recipe["recipe_id"],
            recipe_name="Chicken bowl",
            description=None,
            servings=2,
            meal_type="lunch",
            ingredients=[],
        )
    )
    client.app.dependency_overrides[get_meal_parser] = lambda: parser

    proposed = client.post(
        "/api/v1/chat/messages",
        json={
            "user_id": user["user_id"],
            "message": "two chicken bowls",
            "consumed_at": "2026-08-20T12:00:00",
        },
    )
    assert proposed.status_code == 200
    body = proposed.json()
    assert body["proposal"]["recipe_id"] == recipe["recipe_id"]
    assert body["meal_macros"]["protein_g"] == 40
    assert parser.catalog is not None
    assert client.get(
        "/api/v1/meals",
        params={"user_id": user["user_id"], "day": "2026-08-20"},
    ).json() == []

    confirmed = client.post(
        "/api/v1/chat/confirm", json={"proposal": body["proposal"]}
    )
    assert confirmed.status_code == 200
    result = confirmed.json()
    assert result["created_recipe"] is False
    assert result["daily_protein"]["protein_consumed_g"] == 40


def test_new_recipe_creates_estimated_catalog_records_once(
    client: TestClient,
) -> None:
    user = create_user(client)
    parser = FakeParser(
        ParsedMeal(
            recipe_id=None,
            recipe_name="Tofu scramble",
            description="A tofu breakfast",
            servings=1,
            meal_type="breakfast",
            ingredients=[
                ParsedIngredient(
                    ingredient_id=None,
                    name="Firm tofu",
                    quantity_g=200,
                    calories_per_100g=80,
                    protein_per_100g=10,
                    carbs_per_100g=2,
                    fat_per_100g=4,
                    fiber_per_100g=1,
                )
            ],
        )
    )
    client.app.dependency_overrides[get_meal_parser] = lambda: parser

    proposed = client.post(
        "/api/v1/chat/messages",
        json={
            "user_id": user["user_id"],
            "message": "tofu scramble",
            "consumed_at": datetime(2026, 8, 20, 8).isoformat(),
        },
    )
    assert proposed.status_code == 200
    body = proposed.json()
    assert body["proposal"]["contains_estimates"] is True
    assert client.get("/api/v1/ingredients").json() == []

    first = client.post(
        "/api/v1/chat/confirm", json={"proposal": body["proposal"]}
    )
    assert first.status_code == 200
    assert first.json()["created_recipe"] is True
    assert first.json()["meal_macros"]["protein_g"] == 20

    second = client.post(
        "/api/v1/chat/confirm", json={"proposal": body["proposal"]}
    )
    assert second.status_code == 200
    assert second.json()["created_recipe"] is False

    ingredients = client.get("/api/v1/ingredients").json()
    recipes = client.get("/api/v1/recipes").json()
    assert len(ingredients) == 1
    assert ingredients[0]["nutrition_source"] == "llm_estimate"
    assert len(recipes) == 1


def test_provider_failure_does_not_write_data(client: TestClient) -> None:
    user = create_user(client)
    client.app.dependency_overrides[get_meal_parser] = lambda: FailingParser()

    response = client.post(
        "/api/v1/chat/messages",
        json={"user_id": user["user_id"], "message": "something"},
    )
    assert response.status_code == 503
    assert client.get("/api/v1/ingredients").json() == []
    assert client.get("/api/v1/recipes").json() == []


def test_missing_catalog_id_is_rejected_without_writes(client: TestClient) -> None:
    user = create_user(client)
    parser = FakeParser(
        ParsedMeal(
            recipe_id=None,
            recipe_name="Missing ingredient meal",
            description=None,
            servings=1,
            meal_type="dinner",
            ingredients=[existing_ingredient(999, "Missing", 100)],
        )
    )
    client.app.dependency_overrides[get_meal_parser] = lambda: parser

    response = client.post(
        "/api/v1/chat/messages",
        json={"user_id": user["user_id"], "message": "missing"},
    )
    assert response.status_code == 503
    assert client.get("/api/v1/recipes").json() == []
