from sqlalchemy.orm import Session

from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserRead


class UserService:
    """User profile rules. Protein target calculation lives in the nutrition domain."""

    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)

    def get_user(self, user_id: int) -> UserRead | None:
        user = self.repository.get_by_id(user_id)
        if user is None:
            return None
        return UserRead.model_validate(user)

    def create_user(self, payload: UserCreate) -> UserRead:
        raise NotImplementedError("User creation is not implemented in this scaffold.")
