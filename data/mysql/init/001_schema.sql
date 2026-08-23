-- Baseline schema for a fresh MySQL 8 data directory.
-- Keep this snapshot aligned with Alembic revision 003_scoped_ontology.

CREATE TABLE users (
    user_id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    height_cm NUMERIC(5, 2) NULL,
    weight_kg NUMERIC(5, 2) NULL,
    protein_goal_g NUMERIC(6, 2) NULL,
    calorie_goal NUMERIC(7, 2) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE KEY ix_users_email (email)
) ENGINE=InnoDB;

CREATE TABLE ingredients (
    ingredient_id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    calories_per_100g NUMERIC(8, 2) NOT NULL,
    protein_per_100g NUMERIC(8, 2) NOT NULL,
    carbs_per_100g NUMERIC(8, 2) NOT NULL,
    fat_per_100g NUMERIC(8, 2) NOT NULL,
    fiber_per_100g NUMERIC(8, 2) NOT NULL DEFAULT 0,
    nutrition_source VARCHAR(20) NOT NULL DEFAULT 'manual',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ingredient_id),
    UNIQUE KEY ix_ingredients_name (name)
) ENGINE=InnoDB;

CREATE TABLE recipe_tags (
    tag_id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL,
    PRIMARY KEY (tag_id),
    UNIQUE KEY ix_recipe_tags_name (name)
) ENGINE=InnoDB;

CREATE TABLE recipes (
    recipe_id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    instructions TEXT NULL,
    servings NUMERIC(6, 2) NOT NULL DEFAULT 1,
    created_by INTEGER NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (recipe_id),
    KEY ix_recipes_name (name),
    KEY ix_recipes_created_by (created_by),
    CONSTRAINT fk_recipes_created_by
        FOREIGN KEY (created_by) REFERENCES users (user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE recipe_ingredients (
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity_g NUMERIC(8, 2) NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_id),
    CONSTRAINT uq_recipe_ingredient UNIQUE (recipe_id, ingredient_id),
    CONSTRAINT fk_recipe_ingredients_recipe
        FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id) ON DELETE CASCADE,
    CONSTRAINT fk_recipe_ingredients_ingredient
        FOREIGN KEY (ingredient_id) REFERENCES ingredients (ingredient_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE recipe_tag_mapping (
    recipe_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (recipe_id, tag_id),
    CONSTRAINT fk_recipe_tag_mapping_recipe
        FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id) ON DELETE CASCADE,
    CONSTRAINT fk_recipe_tag_mapping_tag
        FOREIGN KEY (tag_id) REFERENCES recipe_tags (tag_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE meal_logs (
    meal_log_id INTEGER NOT NULL AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    meal_type VARCHAR(20) NOT NULL,
    servings NUMERIC(6, 2) NOT NULL,
    consumed_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (meal_log_id),
    KEY ix_meal_logs_user_id (user_id),
    KEY ix_meal_logs_recipe_id (recipe_id),
    KEY ix_meal_logs_consumed_at (consumed_at),
    KEY ix_meal_logs_user_consumed_at (user_id, consumed_at),
    CONSTRAINT fk_meal_logs_user
        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_meal_logs_recipe
        FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE ontology_entities (
    entity_id VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    kind VARCHAR(64) NOT NULL,
    description TEXT NOT NULL,
    attributes JSON NOT NULL,
    PRIMARY KEY (entity_id),
    KEY ix_ontology_entities_kind (kind)
) ENGINE=InnoDB;

CREATE TABLE ontology_relationships (
    relationship_id VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    source_entity_id VARCHAR(100) NOT NULL,
    target_entity_id VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    PRIMARY KEY (relationship_id),
    KEY ix_ontology_relationships_source_entity_id (source_entity_id),
    KEY ix_ontology_relationships_target_entity_id (target_entity_id),
    CONSTRAINT fk_ontology_relationships_source
        FOREIGN KEY (source_entity_id)
        REFERENCES ontology_entities (entity_id) ON DELETE CASCADE,
    CONSTRAINT fk_ontology_relationships_target
        FOREIGN KEY (target_entity_id)
        REFERENCES ontology_entities (entity_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE ontology_rules (
    rule_id VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    `condition` TEXT NOT NULL,
    effect TEXT NOT NULL,
    PRIMARY KEY (rule_id)
) ENGINE=InnoDB;

CREATE TABLE ontology_entity_scope_allowlist (
    entity_id VARCHAR(100) NOT NULL,
    scope VARCHAR(32) NOT NULL,
    PRIMARY KEY (entity_id, scope),
    CONSTRAINT fk_ontology_entity_scope_entity
        FOREIGN KEY (entity_id)
        REFERENCES ontology_entities (entity_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE ontology_relationship_scope_allowlist (
    relationship_id VARCHAR(100) NOT NULL,
    scope VARCHAR(32) NOT NULL,
    PRIMARY KEY (relationship_id, scope),
    CONSTRAINT fk_ontology_relationship_scope_relationship
        FOREIGN KEY (relationship_id)
        REFERENCES ontology_relationships (relationship_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE ontology_rule_scope_allowlist (
    rule_id VARCHAR(100) NOT NULL,
    scope VARCHAR(32) NOT NULL,
    PRIMARY KEY (rule_id, scope),
    CONSTRAINT fk_ontology_rule_scope_rule
        FOREIGN KEY (rule_id)
        REFERENCES ontology_rules (rule_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    PRIMARY KEY (version_num)
) ENGINE=InnoDB;

INSERT INTO alembic_version (version_num) VALUES ('003_scoped_ontology');
