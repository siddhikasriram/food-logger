"""Load and validate the canonical file-backed food ontology."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.shared.enums import OntologyScope


class _OntologyItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=100, pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    scopes: list[OntologyScope] = Field(min_length=1)

    @field_validator("scopes")
    @classmethod
    def validate_scopes(cls, scopes: list[OntologyScope]) -> list[OntologyScope]:
        if OntologyScope.ALL not in scopes:
            raise ValueError("every ontology item must include the 'all' scope")
        if len(scopes) != len(set(scopes)):
            raise ValueError("ontology item scopes must be unique")
        return scopes


class OntologyEntityDefinition(_OntologyItem):
    kind: str = Field(min_length=1, max_length=64)
    attributes: list[str] = Field(default_factory=list)


class OntologyRelationshipDefinition(_OntologyItem):
    source: str = Field(min_length=1, max_length=100)
    target: str = Field(min_length=1, max_length=100)


class OntologyRuleDefinition(_OntologyItem):
    condition: str = Field(min_length=1)
    effect: str = Field(min_length=1)


class _EntityDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    entities: list[OntologyEntityDefinition]


class _RelationshipDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    relationships: list[OntologyRelationshipDefinition]


class _RuleDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    rules: list[OntologyRuleDefinition]


class OntologyDefinition(BaseModel):
    version: int
    entities: list[OntologyEntityDefinition]
    relationships: list[OntologyRelationshipDefinition]
    rules: list[OntologyRuleDefinition]


def default_ontology_directory() -> Path:
    configured = os.getenv("ONTOLOGY_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[3] / "ontology"


def _read_yaml(path: Path) -> object:
    with path.open(encoding="utf-8") as source:
        return yaml.safe_load(source)


def _assert_unique_ids(items: list[_OntologyItem], label: str) -> None:
    ids = [item.id for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{label} IDs must be unique")


def load_ontology(directory: Path | None = None) -> OntologyDefinition:
    ontology_dir = directory or default_ontology_directory()
    entities = _EntityDocument.model_validate(
        _read_yaml(ontology_dir / "entities.yaml")
    )
    relationships = _RelationshipDocument.model_validate(
        _read_yaml(ontology_dir / "relationships.yaml")
    )
    rules = _RuleDocument.model_validate(_read_yaml(ontology_dir / "rules.yaml"))

    versions = {entities.version, relationships.version, rules.version}
    if len(versions) != 1:
        raise ValueError("ontology files must use the same version")

    _assert_unique_ids(entities.entities, "entity")
    _assert_unique_ids(relationships.relationships, "relationship")
    _assert_unique_ids(rules.rules, "rule")

    entity_ids = {entity.id for entity in entities.entities}
    for relationship in relationships.relationships:
        missing = {
            endpoint
            for endpoint in (relationship.source, relationship.target)
            if endpoint not in entity_ids
        }
        if missing:
            missing_ids = ", ".join(sorted(missing))
            raise ValueError(
                f"relationship '{relationship.id}' references unknown entities: "
                f"{missing_ids}"
            )

    return OntologyDefinition(
        version=versions.pop(),
        entities=entities.entities,
        relationships=relationships.relationships,
        rules=rules.rules,
    )
