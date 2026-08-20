from sqlalchemy.orm import Session

from app.users.models import User, UserIngredientPreference


class UserRepository:
    """Data access for users and ingredient preferences. No business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_preference(
        self, user_id: int, ingredient_id: int
    ) -> UserIngredientPreference | None:
        return (
            self.db.query(UserIngredientPreference)
            .filter(
                UserIngredientPreference.user_id == user_id,
                UserIngredientPreference.ingredient_id == ingredient_id,
            )
            .one_or_none()
        )
