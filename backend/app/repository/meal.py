from datetime import date, datetime, time

from sqlalchemy.orm import Session, joinedload

from app.model.meal import MealLog


class MealLogRepository:
    """Data access for meal logs. Daily totals are derived from these rows, not stored."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, meal_log_id: int) -> MealLog | None:
        return (
            self.db.query(MealLog)
            .options(joinedload(MealLog.recipe))
            .filter(MealLog.meal_log_id == meal_log_id)
            .one_or_none()
        )

    def list_for_user_on_date(self, user_id: int, day: date) -> list[MealLog]:
        start = datetime.combine(day, time.min)
        end = datetime.combine(day, time.max)
        return (
            self.db.query(MealLog)
            .options(joinedload(MealLog.recipe))
            .filter(
                MealLog.user_id == user_id,
                MealLog.consumed_at >= start,
                MealLog.consumed_at <= end,
            )
            .order_by(MealLog.consumed_at)
            .all()
        )

    def add(self, meal_log: MealLog) -> MealLog:
        self.db.add(meal_log)
        self.db.commit()
        self.db.refresh(meal_log)
        loaded = self.get_by_id(meal_log.meal_log_id)
        assert loaded is not None
        return loaded

    def delete(self, meal_log: MealLog) -> None:
        self.db.delete(meal_log)
        self.db.commit()
