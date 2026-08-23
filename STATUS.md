# Project Status

> **Work in progress:** Food Logger is under active development and is not
> production-ready.

Last updated: 2026-08-22

## Current focus

The current development branch is integrating a layered backend architecture,
AI-assisted meal logging, and a canonical food ontology. APIs and data formats
may still change before the first stable release.

## Implemented

- [x] FastAPI backend and React + TypeScript frontend foundations
- [x] User, ingredient, recipe, meal, nutrition, and notification API modules
- [x] Natural-language meal proposal, confirmation, and cancellation flow
- [x] Food-input guardrail and structured meal/ingredient parsing
- [x] Canonical ontology definitions for entities, relationships, and rules
- [x] Scoped ontology API and database synchronization script
- [x] Alembic migration for ontology and scope tables
- [x] Docker Compose development stack

## In progress

- [ ] Complete validation of the backend package reorganization
- [ ] Exercise migrations and ontology seeding against a fresh MySQL database
- [ ] Test the complete chat flow with live model responses
- [ ] Verify Docker startup and frontend/backend integration from a clean checkout
- [ ] Review configuration templates and deployment documentation

## Verification

- [x] Frontend type-check and production build (`npm --prefix frontend run build`)
- [ ] Backend test suite (`pytest`) — requires the dependencies in
  `backend/requirements.txt`; the last local attempt used an older SQLAlchemy
  version that does not provide `DeclarativeBase`
- [ ] Fresh database migration (`alembic upgrade head`)
- [ ] End-to-end Docker smoke test (`docker compose up --build`)

## Known limitations

- Authentication is not implemented; the frontend stores the selected user ID
  in browser local storage.
- Chat conversation state is in memory, expires after 30 minutes by default,
  and is not shared across backend workers.
- AI-generated nutrition values are estimates and require user confirmation.
- The application intentionally does not support water or workout tracking.

## Release readiness

There is no stable release yet. Before tagging one, all verification items
above should pass and the remaining in-progress integration work should be
completed or moved into explicitly tracked follow-up issues.
