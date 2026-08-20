def test_nutrition_service_is_calculation_only() -> None:
    import os

    nutrition_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "app", "nutrition"
    )
    files = os.listdir(nutrition_dir)
    assert "models.py" not in files
    assert "repository.py" not in files
