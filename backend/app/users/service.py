from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.nutrition.service import NutritionService
from app.shared.exceptions import ConflictError, NotFoundError
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserRead, UserUpdate


class UserService:
    """User profile rules. Protein target calculation lives in the nutrition domain."""

    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)
        self.nutrition = NutritionService(db)

    def get_user(self, user_id: int) -> UserRead | None:
        user = self.repository.get_by_id(user_id)
        if user is None:
            return None
        return UserRead.model_validate(user)

    def list_users(self) -> list[UserRead]:
        return [UserRead.model_validate(user) for user in self.repository.list_all()]

    def create_user(self, payload: UserCreate) -> UserRead:
        if self.repository.get_by_email(payload.email) is not None:
            raise ConflictError("A user with this email already exists.")

        protein_goal = payload.protein_goal_g
        if protein_goal is None and payload.weight_kg is not None:
            protein_goal = self.nutrition.recommended_protein_g(payload.weight_kg)

        user = User(
            name=payload.name,
            email=payload.email,
            height_cm=payload.height_cm,
            weight_kg=payload.weight_kg,
            protein_goal_g=protein_goal,
            calorie_goal=payload.calorie_goal,
        )
        try:
            user = self.repository.add(user)
        except IntegrityError as exc:
            self.repository.db.rollback()
            raise ConflictError("A user with this email already exists.") from exc
        return UserRead.model_validate(user)

    def update_user(self, user_id: int, payload: UserUpdate) -> UserRead:
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        user = self.repository.save(user)
        return UserRead.model_validate(user)
