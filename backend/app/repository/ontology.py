from sqlalchemy.orm import Session, selectinload

from app.model.ontology import (
    OntologyEntity,
    OntologyEntityScope,
    OntologyRelationship,
    OntologyRelationshipScope,
    OntologyRule,
    OntologyRuleScope,
)
from app.shared.enums import OntologyScope


class OntologyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_entities(self, scope: OntologyScope) -> list[OntologyEntity]:
        query = self.db.query(OntologyEntity).options(
            selectinload(OntologyEntity.scope_allowlist)
        )
        if scope != OntologyScope.ALL:
            query = query.join(OntologyEntityScope).filter(
                OntologyEntityScope.scope == scope.value
            )
        return query.order_by(OntologyEntity.entity_id).all()

    def list_relationships(
        self, scope: OntologyScope
    ) -> list[OntologyRelationship]:
        query = self.db.query(OntologyRelationship).options(
            selectinload(OntologyRelationship.scope_allowlist)
        )
        if scope != OntologyScope.ALL:
            query = query.join(OntologyRelationshipScope).filter(
                OntologyRelationshipScope.scope == scope.value
            )
        return query.order_by(OntologyRelationship.relationship_id).all()

    def list_rules(self, scope: OntologyScope) -> list[OntologyRule]:
        query = self.db.query(OntologyRule).options(
            selectinload(OntologyRule.scope_allowlist)
        )
        if scope != OntologyScope.ALL:
            query = query.join(OntologyRuleScope).filter(
                OntologyRuleScope.scope == scope.value
            )
        return query.order_by(OntologyRule.rule_id).all()
