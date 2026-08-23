from pathlib import Path
from shutil import copytree

import pytest
import yaml

from app.provider.ontology import default_ontology_directory, load_ontology


def test_load_ontology_validates_canonical_files() -> None:
    ontology = load_ontology()

    assert ontology.version == 1
    assert len(ontology.entities) == 10
    assert len(ontology.relationships) == 10
    assert len(ontology.rules) == 11


def test_load_ontology_rejects_unknown_relationship_endpoint(
    tmp_path: Path,
) -> None:
    ontology_dir = tmp_path / "ontology"
    copytree(default_ontology_directory(), ontology_dir)
    relationships_path = ontology_dir / "relationships.yaml"
    document = yaml.safe_load(relationships_path.read_text(encoding="utf-8"))
    document["relationships"][0]["target"] = "missing_entity"
    relationships_path.write_text(
        yaml.safe_dump(document, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="unknown entities: missing_entity"):
        load_ontology(ontology_dir)


def test_load_ontology_requires_all_scope(tmp_path: Path) -> None:
    ontology_dir = tmp_path / "ontology"
    copytree(default_ontology_directory(), ontology_dir)
    entities_path = ontology_dir / "entities.yaml"
    document = yaml.safe_load(entities_path.read_text(encoding="utf-8"))
    document["entities"][0]["scopes"] = ["logging"]
    entities_path.write_text(
        yaml.safe_dump(document, sort_keys=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="must include the 'all' scope"):
        load_ontology(ontology_dir)
