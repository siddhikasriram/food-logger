def test_user_model_table() -> None:
    from app.model.user import User

    assert User.__tablename__ == "users"
