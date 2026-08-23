from pydantic import BaseModel

from app.shared.enums import OntologyScope


class OntologyEntityRead(BaseModel):
    id: str
    name: str
    kind: str
    description: str
    attributes: list[str]
    scopes: list[OntologyScope]


class OntologyRelationshipRead(BaseModel):
    id: str
    name: str
    source: str
    target: str
    description: str
    scopes: list[OntologyScope]


class OntologyRuleRead(BaseModel):
    id: str
    name: str
    description: str
    condition: str
    effect: str
    scopes: list[OntologyScope]


class OntologyRead(BaseModel):
    version: int
    scope: OntologyScope
    entities: list[OntologyEntityRead]
    relationships: list[OntologyRelationshipRead]
    rules: list[OntologyRuleRead]
