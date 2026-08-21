# food-logger

Nutrition app for logging meals against a shared recipe database and tracking daily protein.

Tech stack: FastAPI, SQLAlchemy, Alembic, MySQL, React + TypeScript.

This application does **not** include water tracking or workout/fitness tracking. Do not add folders, models, services, APIs, or schemas for those domains.

## Repository layout

```
food-logger/
├── backend/                 Python FastAPI application
├── frontend/                Vite + React + TypeScript UI
├── docker-compose.yml       MySQL 8 + backend
├── .env.example             Compose MySQL vars (copy to .env)
└── README.md
```

The frontend talks only to REST endpoints under `/api/v1`. There is no auth; the UI stores the current `user_id` in `localStorage`.

## AI meal chat

The Chat page accepts descriptions such as “I ate two servings of chicken
curry for lunch.” The backend sends the message and the current recipe and
ingredient catalog to OpenAI as context. OpenAI returns structured data; the
backend validates it and performs all nutrition arithmetic deterministically.

Nothing is written until you review the proposed recipe, quantities, meal type,
and macros and select **Confirm and log**. If a recipe or ingredient is missing,
the assistant can propose it. Nutrition values generated for missing
ingredients are stored with an `llm_estimate` source and shown as AI estimates
in the UI. These estimates may be inaccurate and should be reviewed.

Set these values in the root `.env` when using Docker:

```bash
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4.1-mini
```

For a backend process running outside Docker, add the same values to
`backend/.env`. The API key is backend-only and must never be placed in the
frontend environment.

## Backend architecture

Layers inside each domain:

```
routes/controllers  →  services/domain logic  →  repositories/data access  →  SQLAlchemy models  →  MySQL
```

Packages are split by domain, not by technical layer.

| Package | Responsibility |
|---|---|
| `app/core/` | Settings, SQLAlchemy engine/session/`Base`, FastAPI dependencies. No domain rules. |
| `app/shared/` | Exceptions, enums (`MealType`), pagination, quantity/unit helper (grams now, other units later). |
| `app/users/` | User profile (`height_cm`, `weight_kg`, `protein_goal_g`, `calorie_goal`). Calls nutrition for recommended protein; does not implement the formula. |
| `app/nutrition/` | All nutrition math: protein target from weight, ingredient/recipe/meal nutrition, daily consumed/remaining/progress. **No tables** — values are always calculated. |
| `app/ingredients/` | Global shared ingredients. Macros stored **per 100g** only. |
| `app/recipes/` | Global recipes (`created_by` is attribution, not exclusive ownership), `recipe_ingredients` (`quantity_g`), and tags via `recipe_tags` + `recipe_tag_mapping`. |
| `app/meals/` | User meal logs. Source of truth for what was eaten. Daily totals are derived from logs. |
| `app/notifications/` | Stub for future notifications. |
| `app/api/v1/` | Versioned aggregator that mounts domain routers. No business logic. |
| `app/main.py` | FastAPI factory, CORS, `/health`. |
| `alembic/` | Migrations wired to `Base.metadata`. |
| `tests/` | Mirrors domain packages. |

Recipes and ingredients are shared across all users. User-specific data lives only in `users` and `meals`.

## Run locally

Copy the env templates and put real secrets only in the gitignored `.env` files (never commit them):

```bash
cp .env.example .env
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Start the complete app with Docker. Compose reads the repo-root `.env`, applies
database migrations, and starts MySQL, FastAPI, and Vite:

```bash
docker compose up --build
```

UI: http://localhost:5173

API docs: http://localhost:8000/docs

For local development without running the application containers, start only
MySQL:

```bash
docker compose up mysql
```

Then, from `backend/`:

```bash
alembic upgrade head
uvicorn app.main:app --reload
pytest
```

From `frontend/` (Vite proxies `/api` and `/health` to port 8000):

```bash
cd frontend
npm install
npm run dev
```
