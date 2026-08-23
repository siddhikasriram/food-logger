from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.core.database import Base
from app.model.ontology import (
    OntologyEntity,
    OntologyRelationship,
    OntologyRule,
)
from app.provider.ontology_sync import sync_ontology


def test_sync_ontology_is_idempotent() -> None:
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with Session(engine) as db:
        expected = sync_ontology(db)
        db.commit()
        assert sync_ontology(db) == expected
        db.commit()

        assert db.query(OntologyEntity).count() == expected["entities"]
        assert db.query(OntologyRelationship).count() == expected["relationships"]
        assert db.query(OntologyRule).count() == expected["rules"]

    Base.metadata.drop_all(engine)
    engine.dispose()
