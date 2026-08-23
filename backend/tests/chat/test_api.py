from datetime import datetime

from fastapi.testclient import TestClient

from app.provider.conversation_store import ConversationStore
from app.provider.guardrail import (
    InputCategory,
    InputClassification,
)
from app.router.chat import get_conversation_store, get_guardrail, get_meal_assistant
from app.schema.chat import (
    ExtractedFood,
    ExtractedIngredients,
    ParsedIngredient,
)
from app.shared.exceptions import ServiceUnavailableError


class FakeAssistant:
    def __init__(
        self,
        *,
        food_name: str = "Chicken bowl",
        protein_grams: float = 25,
        ingredients: list[ParsedIngredient] | None = None,
    ) -> None:
        self.food_name = food_name
        self.protein_grams = protein_grams
        self.ingredients = ingredients or []
        self.ingredient_catalog: dict[str, object] | None = None

    def extract_food(self, _message: str) -> ExtractedFood:
        return ExtractedFood(
            food_name=self.food_name,
            quantity=1,
            unit="bowl",
            protein_grams=self.protein_grams,
            servings=2,
            meal_type="lunch",
        )

    def extract_ingredients(
        self, _message: str, catalog: dict[str, object]
    ) -> ExtractedIngredients:
        self.ingredient_catalog = catalog
        return ExtractedIngredients(ingredients=self.ingredients)


class FakeGuardrail:
    def __init__(self, category: InputCategory = InputCategory.FOOD) -> None:
        self.category = category

    def classify(self, _message: str) -> InputClassification:
        return InputClassification(category=self.category)


class FailingGuardrail:
    def classify(self, _message: str) -> InputClassification:
        raise ServiceUnavailableError("LLM unavailable")


def configure(
    client: TestClient,
    assistant: FakeAssistant,
    category: InputCategory = InputCategory.FOOD,
) -> ConversationStore:
    store = ConversationStore()
    client.app.dependency_overrides[get_guardrail] = lambda: FakeGuardrail(category)
    client.app.dependency_overrides[get_meal_assistant] = lambda: assistant
    client.app.dependency_overrides[get_conversation_store] = lambda: store
    return store


def create_user(client: TestClient) -> dict:
    return client.post(
        "/api/v1/users",
        json={
            "name": "Ada",
            "email": "ada@example.com",
            "protein_goal_g": 100,
        },
    ).json()


def create_chicken_recipe(client: TestClient) -> dict:
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
    return client.post(
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


def start(client: TestClient, user_id: int, message: str = "two chicken bowls"):
    return client.post(
        "/api/v1/chat/messages",
        json={
            "user_id": user_id,
            "message": message,
            "consumed_at": "2026-08-20T12:00:00",
        },
    )


def continue_conversation(
    client: TestClient, user_id: int, conversation_id: str, message: str
):
    return client.post(
        "/api/v1/chat/messages",
        json={
            "user_id": user_id,
            "conversation_id": conversation_id,
            "message": message,
        },
    )


def test_non_food_is_rejected_without_creating_conversation(
    client: TestClient,
) -> None:
    user = create_user(client)
    configure(client, FakeAssistant(), InputCategory.WATER)

    response = start(client, user["user_id"], "two glasses of water")

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["conversation_id"] is None
    assert client.get(
        "/api/v1/meals",
        params={"user_id": user["user_id"], "day": "2026-08-20"},
    ).json() == []


def test_existing_recipe_requires_confirmation_before_logging(
    client: TestClient,
) -> None:
    user = create_user(client)
    recipe = create_chicken_recipe(client)
    configure(client, FakeAssistant())

    proposed = start(client, user["user_id"])

    assert proposed.status_code == 200
    body = proposed.json()
    assert body["status"] == "awaiting_confirmation"
    assert body["proposal"]["recipe_id"] == recipe["recipe_id"]
    assert body["meal_macros"]["protein_g"] == 40
    assert client.get(
        "/api/v1/meals",
        params={"user_id": user["user_id"], "day": "2026-08-20"},
    ).json() == []

    confirmed = client.post(
        "/api/v1/chat/confirm",
        json={"conversation_id": body["conversation_id"]},
    )

    assert confirmed.status_code == 200
    assert confirmed.json()["created_recipe"] is False
    assert confirmed.json()["daily_protein"]["protein_consumed_g"] == 40


def test_missing_recipe_no_returns_unlogged_projected_summary(
    client: TestClient,
) -> None:
    user = create_user(client)
    configure(
        client,
        FakeAssistant(food_name="Mystery plate", protein_grams=30),
    )
    proposed = start(client, user["user_id"], "mystery plate")
    conversation_id = proposed.json()["conversation_id"]

    skipped = continue_conversation(
        client, user["user_id"], conversation_id, "no"
    )

    assert skipped.status_code == 200
    body = skipped.json()
    assert body["status"] == "summary_only"
    assert body["summary_includes_unlogged_meal"] is True
    assert body["daily_protein"]["protein_consumed_g"] == 30
    assert client.get("/api/v1/recipes").json() == []
    assert client.get(
        "/api/v1/meals",
        params={"user_id": user["user_id"], "day": "2026-08-20"},
    ).json() == []
    assert client.post(
        "/api/v1/chat/confirm", json={"conversation_id": conversation_id}
    ).status_code == 404


def test_missing_recipe_collects_ingredients_then_creates_and_logs(
    client: TestClient,
) -> None:
    user = create_user(client)
    assistant = FakeAssistant(
        food_name="Tofu scramble",
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
    configure(client, assistant)
    proposed = start(client, user["user_id"], "tofu scramble")
    conversation_id = proposed.json()["conversation_id"]

    consent = continue_conversation(
        client, user["user_id"], conversation_id, "yes"
    )
    assert consent.json()["status"] == "awaiting_ingredients"

    ingredients = continue_conversation(
        client, user["user_id"], conversation_id, "200g firm tofu"
    )
    assert ingredients.json()["status"] == "awaiting_confirmation"
    assert ingredients.json()["meal_macros"]["protein_g"] == 40
    assert client.get("/api/v1/ingredients").json() == []
    assert client.get("/api/v1/recipes").json() == []
    assert assistant.ingredient_catalog is not None

    confirmed = client.post(
        "/api/v1/chat/confirm",
        json={"conversation_id": conversation_id},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["created_recipe"] is True
    assert confirmed.json()["meal_macros"]["protein_g"] == 40
    assert client.get("/api/v1/ingredients").json()[0]["nutrition_source"] == "llm_estimate"
    assert len(client.get("/api/v1/recipes").json()) == 1


def test_invalid_consent_and_early_confirmation_preserve_state(
    client: TestClient,
) -> None:
    user = create_user(client)
    configure(client, FakeAssistant(food_name="Unknown meal"))
    proposed = start(client, user["user_id"])
    conversation_id = proposed.json()["conversation_id"]

    unclear = continue_conversation(
        client, user["user_id"], conversation_id, "maybe"
    )
    assert unclear.json()["status"] == "awaiting_recipe_consent"

    early = client.post(
        "/api/v1/chat/confirm", json={"conversation_id": conversation_id}
    )
    assert early.status_code == 400
    consent = continue_conversation(
        client, user["user_id"], conversation_id, "yes"
    )
    assert consent.json()["status"] == "awaiting_ingredients"


def test_cancel_removes_pending_conversation(client: TestClient) -> None:
    user = create_user(client)
    configure(client, FakeAssistant(food_name="Unknown meal"))
    proposed = start(client, user["user_id"])
    conversation_id = proposed.json()["conversation_id"]

    cancelled = client.post(
        "/api/v1/chat/cancel", json={"conversation_id": conversation_id}
    )

    assert cancelled.status_code == 200
    assert client.post(
        "/api/v1/chat/cancel", json={"conversation_id": conversation_id}
    ).status_code == 404


def test_provider_failure_does_not_write_data(client: TestClient) -> None:
    user = create_user(client)
    configure(client, FakeAssistant())
    client.app.dependency_overrides[get_guardrail] = lambda: FailingGuardrail()

    response = start(client, user["user_id"], "something")

    assert response.status_code == 503
    assert client.get("/api/v1/ingredients").json() == []
    assert client.get("/api/v1/recipes").json() == []


def test_expired_conversation_is_rejected(client: TestClient) -> None:
    user = create_user(client)
    now = 0.0
    store = ConversationStore(ttl_seconds=10, clock=lambda: now)
    client.app.dependency_overrides[get_guardrail] = lambda: FakeGuardrail()
    client.app.dependency_overrides[get_meal_assistant] = lambda: FakeAssistant(
        food_name="Unknown meal"
    )
    client.app.dependency_overrides[get_conversation_store] = lambda: store
    proposed = start(client, user["user_id"])
    conversation_id = proposed.json()["conversation_id"]

    now = 11.0
    expired = continue_conversation(
        client, user["user_id"], conversation_id, "yes"
    )

    assert expired.status_code == 404
