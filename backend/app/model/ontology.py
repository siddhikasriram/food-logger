from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OntologyEntity(Base):
    __tablename__ = "ontology_entities"

    entity_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    attributes: Mapped[list[str]] = mapped_column(JSON, nullable=False)

    scope_allowlist: Mapped[list[OntologyEntityScope]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )


class OntologyRelationship(Base):
    __tablename__ = "ontology_relationships"

    relationship_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_entity_id: Mapped[str] = mapped_column(
        ForeignKey("ontology_entities.entity_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_entity_id: Mapped[str] = mapped_column(
        ForeignKey("ontology_entities.entity_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)

    source_entity: Mapped[OntologyEntity] = relationship(
        foreign_keys=[source_entity_id]
    )
    target_entity: Mapped[OntologyEntity] = relationship(
        foreign_keys=[target_entity_id]
    )
    scope_allowlist: Mapped[list[OntologyRelationshipScope]] = relationship(
        back_populates="relationship", cascade="all, delete-orphan"
    )


class OntologyRule(Base):
    __tablename__ = "ontology_rules"

    rule_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    condition: Mapped[str] = mapped_column(Text, nullable=False)
    effect: Mapped[str] = mapped_column(Text, nullable=False)

    scope_allowlist: Mapped[list[OntologyRuleScope]] = relationship(
        back_populates="rule", cascade="all, delete-orphan"
    )


class OntologyEntityScope(Base):
    __tablename__ = "ontology_entity_scope_allowlist"

    entity_id: Mapped[str] = mapped_column(
        ForeignKey("ontology_entities.entity_id", ondelete="CASCADE"),
        primary_key=True,
    )
    scope: Mapped[str] = mapped_column(String(32), primary_key=True)

    entity: Mapped[OntologyEntity] = relationship(back_populates="scope_allowlist")


class OntologyRelationshipScope(Base):
    __tablename__ = "ontology_relationship_scope_allowlist"

    relationship_id: Mapped[str] = mapped_column(
        ForeignKey("ontology_relationships.relationship_id", ondelete="CASCADE"),
        primary_key=True,
    )
    scope: Mapped[str] = mapped_column(String(32), primary_key=True)

    relationship: Mapped[OntologyRelationship] = relationship(
        back_populates="scope_allowlist"
    )


class OntologyRuleScope(Base):
    __tablename__ = "ontology_rule_scope_allowlist"

    rule_id: Mapped[str] = mapped_column(
        ForeignKey("ontology_rules.rule_id", ondelete="CASCADE"),
        primary_key=True,
    )
    scope: Mapped[str] = mapped_column(String(32), primary_key=True)

    rule: Mapped[OntologyRule] = relationship(back_populates="scope_allowlist")
