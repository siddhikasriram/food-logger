from pathlib import Path


def test_nutrition_controller_is_calculation_only() -> None:
    app_dir = Path(__file__).resolve().parents[2] / "app"

    assert not (app_dir / "model" / "nutrition.py").exists()
    assert not (app_dir / "repository" / "nutrition.py").exists()
