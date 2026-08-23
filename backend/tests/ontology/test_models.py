from app.model.ontology import (
    OntologyEntity,
    OntologyEntityScope,
    OntologyRelationship,
    OntologyRelationshipScope,
    OntologyRule,
    OntologyRuleScope,
)


def test_ontology_table_names() -> None:
    assert OntologyEntity.__tablename__ == "ontology_entities"
    assert OntologyRelationship.__tablename__ == "ontology_relationships"
    assert OntologyRule.__tablename__ == "ontology_rules"
    assert (
        OntologyEntityScope.__tablename__
        == "ontology_entity_scope_allowlist"
    )
    assert (
        OntologyRelationshipScope.__tablename__
        == "ontology_relationship_scope_allowlist"
    )
    assert OntologyRuleScope.__tablename__ == "ontology_rule_scope_allowlist"
