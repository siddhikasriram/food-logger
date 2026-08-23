from sqlalchemy.orm import Session

from app.repository.ontology import OntologyRepository
from app.schema.ontology import (
    OntologyEntityRead,
    OntologyRead,
    OntologyRelationshipRead,
    OntologyRuleRead,
)
from app.shared.enums import OntologyScope


class OntologyController:
    def __init__(self, db: Session) -> None:
        self.repository = OntologyRepository(db)

    def get_ontology(self, scope: OntologyScope) -> OntologyRead:
        entities = self.repository.list_entities(scope)
        relationships = self.repository.list_relationships(scope)
        rules = self.repository.list_rules(scope)
        versions = {
            item.version for item in [*entities, *relationships, *rules]
        }

        return OntologyRead(
            version=max(versions, default=1),
            scope=scope,
            entities=[
                OntologyEntityRead(
                    id=item.entity_id,
                    name=item.name,
                    kind=item.kind,
                    description=item.description,
                    attributes=item.attributes,
                    scopes=sorted(
                        (OntologyScope(row.scope) for row in item.scope_allowlist),
                        key=lambda value: value.value,
                    ),
                )
                for item in entities
            ],
            relationships=[
                OntologyRelationshipRead(
                    id=item.relationship_id,
                    name=item.name,
                    source=item.source_entity_id,
                    target=item.target_entity_id,
                    description=item.description,
                    scopes=sorted(
                        (OntologyScope(row.scope) for row in item.scope_allowlist),
                        key=lambda value: value.value,
                    ),
                )
                for item in relationships
            ],
            rules=[
                OntologyRuleRead(
                    id=item.rule_id,
                    name=item.name,
                    description=item.description,
                    condition=item.condition,
                    effect=item.effect,
                    scopes=sorted(
                        (OntologyScope(row.scope) for row in item.scope_allowlist),
                        key=lambda value: value.value,
                    ),
                )
                for item in rules
            ],
        )
