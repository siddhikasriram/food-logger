# food-logger

> **Work in progress:** This project is under active development and is not
> production-ready. See [STATUS.md](STATUS.md) for current progress, verification
> results, and known limitations.

Nutrition app for logging meals against a shared recipe database and tracking daily protein.

Tech stack: FastAPI, SQLAlchemy, Alembic, MySQL, React + TypeScript.

This application does **not** include water tracking or workout/fitness tracking. Do not add folders, models, services, APIs, or schemas for those domains.

## Repository layout

```
food-logger/
├── backend/                 Python FastAPI application
├── data/mysql/              MySQL schema, seed SQL, and local data directory
├── frontend/                Vite + React + TypeScript UI
├── ontology/                Canonical food ontology markdown and YAML
├── docker-compose.yml       MySQL 8 + backend
├── .env.example             Compose MySQL vars (copy to .env)
├── STATUS.md                Development progress and release readiness
└── README.md
```

The frontend talks only to REST endpoints under `/api/v1`. There is no auth; the UI stores the current `user_id` in `localStorage`.

## AI meal chat

The Chat page accepts descriptions such as “I ate two servings of chicken
curry for lunch.” OpenAI first classifies food versus workout, water, or other
input, then extracts structured food fields. Recipe lookup, nutrition
arithmetic, daily aggregation, and database writes are deterministic.

When a recipe is missing, the assistant asks whether to add it. Choosing
**Add recipe** starts a second turn that collects and structures ingredients;
there is intentionally no ontology-validation step. Choosing **Don’t add**
returns a projected protein summary that includes the extracted meal estimate,
but does not save the meal or recipe.

Found and newly prepared recipes both require **Confirm and log** before
anything is written. Nutrition values generated for missing ingredients are
stored with an `llm_estimate` source and shown as AI estimates in the UI.
These estimates may be inaccurate and should be reviewed.

Multi-turn state is held in backend memory and identified by
`conversation_id`. It expires after 30 minutes by default, is lost when the
backend restarts, and is not shared between multiple backend worker processes.
`POST /api/v1/chat/cancel` explicitly discards pending state.

Set these values in the root `.env` when using Docker:

```bash
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4.1-mini
CHAT_CONVERSATION_TTL_SECONDS=1800
```

For a backend process running outside Docker, add the same values to
`backend/.env`. The API key is backend-only and must never be placed in the
frontend environment.

## Food ontology

The root `ontology/` directory is the canonical source for domain entities,
relationships, and deterministic rules:

- `food_ontology.md` documents the contract.
- `entities.yaml`, `relationships.yaml`, and `rules.yaml` contain the
  machine-readable definitions.

`python -m app.provider.ontology_sync` validates these files and synchronizes normalized
ontology tables plus explicit scope-allowlist tables. Synchronization is
idempotent: canonical values and scope mappings are updated, new IDs are
inserted, and IDs removed from YAML are deleted.

The ontology is exposed as typed JSON:

```text
GET /api/v1/ontology?scope=all
GET /api/v1/ontology?scope=logging
```

`all` returns the complete ontology. `logging` returns only entities,
relationships, and rules tagged with the logging scope in YAML. The query scope
filters content; it is not an authentication permission. Omitting `scope`
defaults to `all`, and unsupported values return HTTP 422.

When running the backend outside the repository layout, set `ONTOLOGY_DIR` to
the directory containing the three YAML files.

## Backend architecture

The backend is organized by technical layer:

```
routers  →  controllers/domain logic  →  repositories/data access  →  SQLAlchemy models  →  MySQL
```

| Package | Responsibility |
|---|---|
| `app/core/` | Settings, SQLAlchemy engine/session/`Base`, FastAPI dependencies. No domain rules. |
| `app/model/` | SQLAlchemy entities grouped into domain-named modules. Nutrition and notifications intentionally have no tables. |
| `app/schema/` | Pydantic request, response, and shared schemas. |
| `app/controller/` | Business rules for users, ingredients, recipes, meals, nutrition, chat, and notifications. |
| `app/router/` | FastAPI endpoint modules and the versioned router aggregator. No business logic. |
| `app/repository/` | Data access for users, ingredients, recipes, and meal logs. |
| `app/provider/` | External integrations such as the OpenAI meal parser. |
| `app/shared/` | Cross-cutting exceptions and enums such as `MealType`. |
| `app/main.py` | FastAPI factory, CORS, `/health`. |
| `alembic/` | Migrations wired to `Base.metadata`. |
| `tests/` | Backend API, model, provider, and package tests. |

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

Start the complete app with Docker. Compose reads the repo-root `.env`,
initializes a new MySQL data directory, applies later database migrations, and
starts MySQL, FastAPI, and Vite:

```bash
docker compose up --build
```

UI: http://localhost:5173

API docs: http://localhost:8000/docs

### Demo data

MySQL runs the tracked files in `data/mysql/init/` in filename order when
`data/mysql/db/` is empty:

- `001_schema.sql` creates the current schema and stamps Alembic at
  `003_scoped_ontology`.
- `002_seed.sql` loads a shared ingredient and recipe catalog plus seven days
  of meal history for:
  - Alex Demo (`alex.demo@foodlogger.local`)
  - Maya Demo (`maya.demo@foodlogger.local`)

The generated MySQL files persist in the gitignored `data/mysql/db/` directory.
MySQL init scripts do not run again on normal container restarts. To initialize
from scratch, stop the stack and clear that directory only after backing up any
data you need.

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
