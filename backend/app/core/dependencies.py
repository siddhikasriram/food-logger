from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.database import get_db


def db_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy session."""
    yield from get_db()
