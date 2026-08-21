def test_user_model_table() -> None:
    from app.users.models import User

    assert User.__tablename__ == "users"
