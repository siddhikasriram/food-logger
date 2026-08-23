-- Full demo dataset for a newly initialized database.

START TRANSACTION;

INSERT INTO users (
    user_id, name, email, height_cm, weight_kg, protein_goal_g, calorie_goal
) VALUES
    (1, 'Alex Demo', 'alex.demo@foodlogger.local', 178, 78, 125, 2300),
    (2, 'Maya Demo', 'maya.demo@foodlogger.local', 165, 62, 100, 1900);

INSERT INTO ingredients (
    ingredient_id,
    name,
    calories_per_100g,
    protein_per_100g,
    carbs_per_100g,
    fat_per_100g,
    fiber_per_100g,
    nutrition_source
) VALUES
    (1, 'Greek Yogurt', 59, 10.3, 3.6, 0.4, 0, 'manual'),
    (2, 'Mixed Berries', 50, 0.7, 12, 0.3, 2.4, 'manual'),
    (3, 'Rolled Oats', 389, 16.9, 66.3, 6.9, 10.6, 'manual'),
    (4, 'Chia Seeds', 486, 16.5, 42.1, 30.7, 34.4, 'manual'),
    (5, 'Chicken Breast', 165, 31, 0, 3.6, 0, 'manual'),
    (6, 'Brown Rice, Cooked', 123, 2.7, 25.6, 1, 1.6, 'manual'),
    (7, 'Broccoli', 35, 2.4, 7.2, 0.4, 3.3, 'manual'),
    (8, 'Olive Oil', 884, 0, 0, 100, 0, 'manual'),
    (9, 'Lentils, Cooked', 116, 9, 20.1, 0.4, 7.9, 'manual'),
    (10, 'Tomatoes', 18, 0.9, 3.9, 0.2, 1.2, 'manual'),
    (11, 'Spinach', 23, 2.9, 3.6, 0.4, 2.2, 'manual'),
    (12, 'Coconut Milk', 197, 2, 2.8, 21.3, 0, 'manual'),
    (13, 'Salmon', 208, 20.4, 0, 13.4, 0, 'manual'),
    (14, 'Sweet Potato', 90, 2, 20.7, 0.2, 3.3, 'manual'),
    (15, 'Firm Tofu', 144, 17.3, 2.8, 8.7, 2.3, 'manual'),
    (16, 'Bell Pepper', 31, 1, 6, 0.3, 2.1, 'manual'),
    (17, 'Soy Sauce', 53, 8.1, 4.9, 0.6, 0.8, 'manual'),
    (18, 'Whole Wheat Tortilla', 312, 9.6, 52.1, 8.3, 8.3, 'manual'),
    (19, 'Turkey Breast', 135, 30, 0, 1, 0, 'manual'),
    (20, 'Avocado', 160, 2, 8.5, 14.7, 6.7, 'manual'),
    (21, 'Peanut Butter', 588, 25, 20, 50, 6, 'manual'),
    (22, 'Banana', 89, 1.1, 22.8, 0.3, 2.6, 'manual');

INSERT INTO recipe_tags (tag_id, name) VALUES
    (1, 'Breakfast'),
    (2, 'Lunch'),
    (3, 'Dinner'),
    (4, 'High Protein'),
    (5, 'Vegetarian'),
    (6, 'Vegan'),
    (7, 'Quick');

INSERT INTO recipes (
    recipe_id, name, description, instructions, servings, created_by
) VALUES
    (
        1,
        'Greek Yogurt Berry Parfait',
        'Creamy yogurt layered with berries, oats, and chia seeds.',
        'Layer all ingredients in a bowl or jar and serve.',
        1,
        1
    ),
    (
        2,
        'Chicken Brown Rice Bowl',
        'A balanced chicken, rice, and broccoli meal.',
        'Grill the chicken, steam the broccoli, and serve over warm rice.',
        1,
        1
    ),
    (
        3,
        'Lentil Vegetable Curry',
        'A hearty plant-based curry with lentils and greens.',
        'Simmer the vegetables, lentils, and coconut milk until thick; serve with rice.',
        1,
        2
    ),
    (
        4,
        'Salmon Sweet Potato Plate',
        'Roasted salmon with sweet potato and broccoli.',
        'Roast the salmon and vegetables with olive oil until cooked through.',
        1,
        1
    ),
    (
        5,
        'Tofu Vegetable Stir-Fry',
        'Crisp tofu and colorful vegetables over brown rice.',
        'Saute tofu and vegetables, add soy sauce, and serve over rice.',
        1,
        2
    ),
    (
        6,
        'Turkey Avocado Wrap',
        'A quick whole-wheat wrap with lean turkey and avocado.',
        'Fill the tortilla with turkey, avocado, spinach, and tomato; roll tightly.',
        1,
        1
    ),
    (
        7,
        'Peanut Butter Banana Oatmeal',
        'Warm oats topped with banana, peanut butter, and chia.',
        'Cook the oats with water, then stir in the remaining ingredients.',
        1,
        2
    );

INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity_g) VALUES
    (1, 1, 200), (1, 2, 100), (1, 3, 40), (1, 4, 10),
    (2, 5, 180), (2, 6, 180), (2, 7, 120), (2, 8, 10),
    (3, 6, 150), (3, 9, 200), (3, 10, 150), (3, 11, 80), (3, 12, 80),
    (4, 7, 120), (4, 8, 10), (4, 13, 170), (4, 14, 220),
    (5, 6, 160), (5, 7, 120), (5, 8, 8), (5, 15, 180), (5, 16, 120), (5, 17, 20),
    (6, 10, 60), (6, 11, 30), (6, 18, 65), (6, 19, 120), (6, 20, 60),
    (7, 3, 60), (7, 4, 10), (7, 21, 20), (7, 22, 120);

INSERT INTO recipe_tag_mapping (recipe_id, tag_id) VALUES
    (1, 1), (1, 4), (1, 5), (1, 7),
    (2, 2), (2, 3), (2, 4),
    (3, 2), (3, 3), (3, 5), (3, 6),
    (4, 3), (4, 4),
    (5, 2), (5, 3), (5, 5), (5, 6),
    (6, 2), (6, 4), (6, 7),
    (7, 1), (7, 5), (7, 6), (7, 7);

CREATE TEMPORARY TABLE seed_day_offsets (
    day_offset INTEGER NOT NULL PRIMARY KEY
);

INSERT INTO seed_day_offsets (day_offset)
VALUES (0), (1), (2), (3), (4), (5), (6);

CREATE TEMPORARY TABLE seed_meal_schedule (
    user_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    meal_type VARCHAR(20) NOT NULL,
    servings NUMERIC(6, 2) NOT NULL,
    consumed_time TIME NOT NULL
);

-- SQLAlchemy persists MealType enum member names in this column.
INSERT INTO seed_meal_schedule (
    user_id, recipe_id, meal_type, servings, consumed_time
) VALUES
    (1, 1, 'BREAKFAST', 1, '08:00:00'),
    (1, 6, 'LUNCH', 1, '12:30:00'),
    (1, 1, 'SNACK', 0.5, '15:30:00'),
    (1, 2, 'DINNER', 1, '18:30:00'),
    (2, 7, 'BREAKFAST', 1, '07:45:00'),
    (2, 5, 'LUNCH', 1, '12:15:00'),
    (2, 3, 'DINNER', 1, '18:45:00');

INSERT INTO meal_logs (
    user_id, recipe_id, meal_type, servings, consumed_at
)
SELECT
    schedule.user_id,
    schedule.recipe_id,
    schedule.meal_type,
    schedule.servings,
    TIMESTAMP(
        DATE_SUB(CURRENT_DATE(), INTERVAL offsets.day_offset DAY),
        schedule.consumed_time
    )
FROM seed_day_offsets AS offsets
CROSS JOIN seed_meal_schedule AS schedule;

DROP TEMPORARY TABLE seed_meal_schedule;
DROP TEMPORARY TABLE seed_day_offsets;

COMMIT;
