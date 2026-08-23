from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.controller.ontology import OntologyController
from app.core.dependencies import db_session
from app.schema.ontology import OntologyRead
from app.shared.enums import OntologyScope

router = APIRouter(prefix="/ontology", tags=["ontology"])


def get_ontology_controller(
    db: Session = Depends(db_session),
) -> OntologyController:
    return OntologyController(db)


@router.get("", response_model=OntologyRead)
def get_ontology(
    scope: OntologyScope = Query(default=OntologyScope.ALL),
    controller: OntologyController = Depends(get_ontology_controller),
) -> OntologyRead:
    return controller.get_ontology(scope)
