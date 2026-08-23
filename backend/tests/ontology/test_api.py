def test_all_scope_returns_complete_ontology(client) -> None:
    response = client.get("/api/v1/ontology", params={"scope": "all"})

    assert response.status_code == 200
    body = response.json()
    assert body["version"] == 1
    assert body["scope"] == "all"
    assert len(body["entities"]) == 10
    assert len(body["relationships"]) == 10
    assert len(body["rules"]) == 11
    assert "recipe_tag" in {item["id"] for item in body["entities"]}


def test_logging_scope_returns_only_allowlisted_items(client) -> None:
    response = client.get("/api/v1/ontology", params={"scope": "logging"})

    assert response.status_code == 200
    body = response.json()
    assert body["scope"] == "logging"
    assert len(body["entities"]) == 9
    assert len(body["relationships"]) == 8
    assert len(body["rules"]) == 9
    assert "recipe_tag" not in {item["id"] for item in body["entities"]}
    assert "recipe_has_tag" not in {
        item["id"] for item in body["relationships"]
    }
    assert "shared_recipe_visibility" not in {
        item["id"] for item in body["rules"]
    }
    assert all(
        "logging" in item["scopes"]
        for collection in ("entities", "relationships", "rules")
        for item in body[collection]
    )


def test_ontology_defaults_to_all_scope(client) -> None:
    response = client.get("/api/v1/ontology")

    assert response.status_code == 200
    assert response.json()["scope"] == "all"


def test_ontology_rejects_unknown_scope(client) -> None:
    response = client.get("/api/v1/ontology", params={"scope": "admin"})

    assert response.status_code == 422
