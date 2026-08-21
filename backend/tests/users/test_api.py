from fastapi.testclient import TestClient


def test_create_user_sets_protein_goal_from_weight(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users",
        json={"name": "Ada", "email": "ada@example.com", "weight_kg": 70},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Ada"
    assert body["protein_goal_g"] == 98.0


def test_duplicate_email_returns_409(client: TestClient) -> None:
    payload = {"name": "Ada", "email": "ada@example.com"}
    assert client.post("/api/v1/users", json=payload).status_code == 201
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 409
    assert "email" in response.json()["detail"].lower()


def test_get_missing_user_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/users/999")
    assert response.status_code == 404
