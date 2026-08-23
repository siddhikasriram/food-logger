"""Add normalized ontology and scope allowlist tables.

Revision ID: 003_scoped_ontology
Revises: 002_nutrition_source
Create Date: 2026-08-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_scoped_ontology"
down_revision: Union[str, Sequence[str], None] = "002_nutrition_source"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ontology_entities",
        sa.Column("entity_id", sa.String(length=100), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("entity_id"),
    )
    op.create_index(
        op.f("ix_ontology_entities_kind"),
        "ontology_entities",
        ["kind"],
        unique=False,
    )

    op.create_table(
        "ontology_relationships",
        sa.Column("relationship_id", sa.String(length=100), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_entity_id", sa.String(length=100), nullable=False),
        sa.Column("target_entity_id", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["source_entity_id"], ["ontology_entities.entity_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["target_entity_id"], ["ontology_entities.entity_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("relationship_id"),
    )
    op.create_index(
        op.f("ix_ontology_relationships_source_entity_id"),
        "ontology_relationships",
        ["source_entity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ontology_relationships_target_entity_id"),
        "ontology_relationships",
        ["target_entity_id"],
        unique=False,
    )

    op.create_table(
        "ontology_rules",
        sa.Column("rule_id", sa.String(length=100), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("condition", sa.Text(), nullable=False),
        sa.Column("effect", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("rule_id"),
    )

    op.create_table(
        "ontology_entity_scope_allowlist",
        sa.Column("entity_id", sa.String(length=100), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"], ["ontology_entities.entity_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("entity_id", "scope"),
    )
    op.create_table(
        "ontology_relationship_scope_allowlist",
        sa.Column("relationship_id", sa.String(length=100), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(
            ["relationship_id"],
            ["ontology_relationships.relationship_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("relationship_id", "scope"),
    )
    op.create_table(
        "ontology_rule_scope_allowlist",
        sa.Column("rule_id", sa.String(length=100), nullable=False),
        sa.Column("scope", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(
            ["rule_id"], ["ontology_rules.rule_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("rule_id", "scope"),
    )


def downgrade() -> None:
    op.drop_table("ontology_rule_scope_allowlist")
    op.drop_table("ontology_relationship_scope_allowlist")
    op.drop_table("ontology_entity_scope_allowlist")
    op.drop_table("ontology_rules")
    op.drop_index(
        op.f("ix_ontology_relationships_target_entity_id"),
        table_name="ontology_relationships",
    )
    op.drop_index(
        op.f("ix_ontology_relationships_source_entity_id"),
        table_name="ontology_relationships",
    )
    op.drop_table("ontology_relationships")
    op.drop_index(op.f("ix_ontology_entities_kind"), table_name="ontology_entities")
    op.drop_table("ontology_entities")
