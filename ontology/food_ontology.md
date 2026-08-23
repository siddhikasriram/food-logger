# Food Logger Ontology

This ontology defines the concepts, relationships, and deterministic rules used
by the food logger. The YAML files in this directory are the canonical,
machine-readable source. Database tables are synchronized from them by
`python -m app.provider.ontology_sync`.

## Scopes

- `all` contains every ontology item.
- `logging` is the allowlisted subset needed to parse, validate, and persist a
  meal log.

Every item must include `all`. An item is returned by the logging API only when
it also includes `logging`.

## Files

- `entities.yaml` defines domain concepts and their relevant attributes.
- `relationships.yaml` defines directed links between entity concepts.
- `rules.yaml` defines validation and calculation constraints.

Stable string IDs are API and database identifiers. Rename a label or
description without changing its ID. Removing an ID from a YAML file removes it
and its scope mappings from the synchronized ontology tables on the next seed.

## API

The read-only endpoint is:

```text
GET /api/v1/ontology?scope=all
GET /api/v1/ontology?scope=logging
```

Scopes filter content; they are not authentication permissions.
