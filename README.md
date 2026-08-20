# food-logger

Nutrition app for logging meals against a shared recipe database and tracking daily protein.

Tech stack: FastAPI, SQLAlchemy, Alembic, MySQL, React + TypeScript (frontend not started).

This application does **not** include water tracking or workout/fitness tracking. Do not add folders, models, services, APIs, or schemas for those domains.

## Repository layout

```
food-logger/
├── backend/                 Python FastAPI application
├── docker-compose.yml       MySQL 8 + backend
└── README.md
```

The frontend will live at the repo root later. It should talk only to REST endpoints under `/api/v1`.

## Backend architecture

Layers inside each domain:

```
routes/controllers  →  services/domain logic  →  repositories/data access  →  SQLAlchemy models  →  MySQL
```

Packages are split by domain, not by technical layer.

| Package | Responsibility |
|---|---|
| `app/core/` | Settings, SQLAlchemy engine/session/`Base`, FastAPI dependencies. No domain rules. |
| `app/shared/` | Exceptions, enums (`MealType`, `IngredientPreference`), pagination, quantity/unit helper (grams now, other units later). |
| `app/users/` | User profile (`height_cm`, `weight_kg`, `protein_goal_g`, `calorie_goal`) and `user_ingredient_preferences`. Calls nutrition for recommended protein; does not implement the formula. |
| `app/nutrition/` | All nutrition math: protein target from weight, ingredient/recipe/meal nutrition, daily consumed/remaining/progress. **No tables** — values are always calculated. |
| `app/ingredients/` | Global shared ingredients. Macros stored **per 100g** only. |
| `app/recipes/` | Global recipes (`created_by` is attribution, not exclusive ownership), `recipe_ingredients` (`quantity_g`), and tags via `recipe_tags` + `recipe_tag_mapping`. |
| `app/meals/` | User meal logs. Source of truth for what was eaten. Daily totals are derived from logs. |
| `app/notifications/` | Stub for future notifications. |
| `app/api/v1/` | Versioned aggregator that mounts domain routers. No business logic. |
| `app/main.py` | FastAPI factory, CORS, `/health`. |
| `alembic/` | Migrations wired to `Base.metadata`. No table revisions in this scaffold. |
| `tests/` | Mirrors domain packages. |

Recipes and ingredients are shared across all users. User-specific data lives only in `users` and `meals`.

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Start MySQL (and optionally the API) with Docker:

```bash
docker compose up mysql
# or: docker compose up
```

From `backend/`:

```bash
uvicorn app.main:app --reload
pytest
```

API docs: http://localhost:8000/docs

This scaffold wires the module layout and model shells. CRUD, nutrition algorithms, and Alembic table migrations are not implemented yet.
