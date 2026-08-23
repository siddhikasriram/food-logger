"""Synchronize the canonical YAML ontology into normalized database tables."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.model.ontology import (
    OntologyEntity,
    OntologyEntityScope,
    OntologyRelationship,
    OntologyRelationshipScope,
    OntologyRule,
    OntologyRuleScope,
)
from app.provider.ontology import OntologyDefinition, load_ontology


def _sync_entities(db: Session, definition: OntologyDefinition) -> None:
    definitions = {item.id: item for item in definition.entities}
    existing = {
        item.entity_id: item for item in db.query(OntologyEntity).all()
    }

    for entity_id, entity in existing.items():
        if entity_id not in definitions:
            db.delete(entity)

    for entity_id, item in definitions.items():
        entity = existing.get(entity_id)
        if entity is None:
            entity = OntologyEntity(entity_id=entity_id)
            db.add(entity)
        entity.version = definition.version
        entity.name = item.name
        entity.kind = item.kind
        entity.description = item.description
        entity.attributes = item.attributes
        entity.scope_allowlist = [
            OntologyEntityScope(scope=scope.value) for scope in item.scopes
        ]


def _sync_relationships(db: Session, definition: OntologyDefinition) -> None:
    definitions = {item.id: item for item in definition.relationships}
    existing = {
        item.relationship_id: item
        for item in db.query(OntologyRelationship).all()
    }

    recreate: set[str] = set()
    for relationship_id, relationship in existing.items():
        item = definitions.get(relationship_id)
        if item is None:
            db.delete(relationship)
            continue
        if (
            relationship.source_entity_id != item.source
            or relationship.target_entity_id != item.target
        ):
            db.delete(relationship)
            recreate.add(relationship_id)

    db.flush()
    for relationship_id in recreate:
        existing.pop(relationship_id)
    for relationship_id, item in definitions.items():
        relationship = existing.get(relationship_id)
        if relationship is None:
            relationship = OntologyRelationship(
                relationship_id=relationship_id
            )
            db.add(relationship)
        relationship.version = definition.version
        relationship.name = item.name
        relationship.source_entity_id = item.source
        relationship.target_entity_id = item.target
        relationship.description = item.description
        relationship.scope_allowlist = [
            OntologyRelationshipScope(scope=scope.value)
            for scope in item.scopes
        ]


def _sync_rules(db: Session, definition: OntologyDefinition) -> None:
    definitions = {item.id: item for item in definition.rules}
    existing = {item.rule_id: item for item in db.query(OntologyRule).all()}

    for rule_id, rule in existing.items():
        if rule_id not in definitions:
            db.delete(rule)

    for rule_id, item in definitions.items():
        rule = existing.get(rule_id)
        if rule is None:
            rule = OntologyRule(rule_id=rule_id)
            db.add(rule)
        rule.version = definition.version
        rule.name = item.name
        rule.description = item.description
        rule.condition = item.condition
        rule.effect = item.effect
        rule.scope_allowlist = [
            OntologyRuleScope(scope=scope.value) for scope in item.scopes
        ]


def sync_ontology(db: Session, directory: Path | None = None) -> dict[str, int]:
    """Make database ontology rows match the canonical YAML definitions."""
    definition = load_ontology(directory)

    relationship_definitions = {
        item.id: item for item in definition.relationships
    }
    for relationship in db.query(OntologyRelationship).all():
        item = relationship_definitions.get(relationship.relationship_id)
        if (
            item is None
            or relationship.source_entity_id != item.source
            or relationship.target_entity_id != item.target
        ):
            db.delete(relationship)
    db.flush()

    _sync_entities(db, definition)
    db.flush()
    _sync_relationships(db, definition)
    _sync_rules(db, definition)
    db.flush()

    return {
        "entities": len(definition.entities),
        "relationships": len(definition.relationships),
        "rules": len(definition.rules),
    }


def main() -> None:
    db = SessionLocal()
    try:
        counts = sync_ontology(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(
        "Ontology sync complete: "
        + ", ".join(f"{name}={count}" for name, count in counts.items())
    )


if __name__ == "__main__":
    main()
