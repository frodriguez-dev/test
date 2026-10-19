# Architecture decisions

Fundamental decisions for this repository, recorded so future work can follow
them without re-litigating settled questions. Each entry states the context, the
decision, and its consequences. Append new entries with the next number; do not
rewrite accepted decisions. Supersede one explicitly when it changes.

## 0001 — Monorepo with separate frontend and backend

- **Status:** Accepted
- **Date:** 2026-10-19
- **Issue:** #16

**Context.** The repository will host a full stack application built with React
and Django. Both parts are developed together but deployed separately.

**Decision.** Use a single repository with two top-level application
directories and shared documentation:

```
frontend/   React single-page application
backend/    Django REST API and PostgreSQL access
docs/       Architecture decisions, conventions, and AI guidance
```

Each application keeps its own manifest and lock file. There is no shared
runtime code between them.

**Consequences.**

- One clone and one pull request can change both sides of a feature.
- Frontend and backend dependencies stay isolated and can be released
  independently.
- Shared contracts must be documented (currently the REST API) rather than
  imported across the boundary.
- A root-level task runner is intentionally absent until a concrete need appears.

## 0002 — React, TypeScript, Vite, and pnpm for the frontend

- **Status:** Accepted, not yet initialized (issue #18)
- **Date:** 2026-10-19
- **Issue:** #16

**Context.** The frontend needs a small, fast toolchain with strong typing and a
predictable developer experience.

**Decision.** Build the frontend with React and TypeScript, bundling with Vite
and managing dependencies with pnpm. Strict TypeScript is enabled by default.

**Consequences.**

- The app is a static bundle that talks to the backend over HTTP.
- Server-side rendering is out of scope for now.
- `package.json` and `pnpm-lock.yaml` live in `frontend/`; no Node tooling is
  required at the repository root.
- Exact versions and scripts are chosen when issue #18 initializes the project.

## 0003 — Django, DRF, PostgreSQL, and uv for the backend

- **Status:** Accepted, not yet initialized (issue #17)
- **Date:** 2026-10-19
- **Issue:** #16

**Context.** The backend must expose a JSON API, model relational data, and stay
simple to operate and test.

**Decision.** Use Django with Django REST Framework for the API, PostgreSQL as
the only database, and uv for dependency and environment management.

**Consequences.**

- Domain state is modeled with Django apps and migrations.
- The API is REST/JSON; GraphQL and a separate ORM layer are out of scope.
- `pyproject.toml` and `uv.lock` will live in `backend/` once issue #17
  initializes the project. The current root `pyproject.toml` is provisional and
  is retained until then.
- PostgreSQL-specific features are allowed when they simplify the data model,
  but local development must use PostgreSQL too, not SQLite.

## 0004 — Layered responsibilities and dependency direction

- **Status:** Accepted
- **Date:** 2026-10-19
- **Issue:** #16

**Context.** Without explicit boundaries, a monorepo tends to accumulate
circular imports and business logic in controllers or UI components.

**Decision.** Keep four areas with one-directional dependencies:

```
frontend UI  →  frontend API client  →  HTTP /api/v1/  →  backend views
                                                          → serializers/services
                                                          → models → PostgreSQL
```

- Backend views handle HTTP concerns only; validation and workflows live in
  serializers, services, or model methods.
- The frontend `src/api/` module is the only place that performs HTTP calls.
- Frontend `pages` compose `features`, which compose shared `components` and
  `lib`. Shared code never imports pages or features.
- PostgreSQL is reached only through backend models and queries; the frontend
  has no direct database access.

**Consequences.**

- Features can be changed on one side behind a stable API contract.
- Cross-app reads in Django go through the owning app's Python API, not raw SQL
  against its tables.
- Layers may be skipped for trivial cases, but dependencies must not point
  upward.

## 0005 — Versioned REST API as the application contract

- **Status:** Accepted
- **Date:** 2026-10-19
- **Issue:** #16

**Context.** Frontend and backend are separate applications and need an explicit
contract.

**Decision.** Expose the API under `/api/v1/`, use JSON, and follow DRF
conventions for status codes and error bodies. In development, the Vite dev
server proxies `/api` to the Django server so the frontend uses relative URLs.

**Consequences.**

- Breaking changes require a new API version or a coordinated change in both
  applications.
- CORS is unnecessary in local development when the proxy is used; production
  deployment decides its own origin strategy.
- API documentation will be added when the first endpoints exist; the format is
  **PENDING**.

## 0006 — Configuration through environment variables

- **Status:** Accepted
- **Date:** 2026-10-19
- **Issue:** #16

**Context.** Both applications need environment-specific settings without
committing secrets.

**Decision.** Read configuration from environment variables. Commit only
`.env.example` files with variable names and safe defaults; ignore real `.env`
files. Frontend variables are limited to public values exposed by Vite.

**Consequences.**

- The same code runs locally and in deployment with different configuration.
- `DEBUG`, database credentials, and secret keys never appear in Git.
- Each application documents its own variables next to its `.env.example`.

## 0007 — Documentation is part of the repository

- **Status:** Accepted
- **Date:** 2026-10-19
- **Issue:** #16

**Context.** Architecture and conventions must stay usable by humans and AI
agents and must not be duplicated across files.

**Decision.** Keep architecture in [`docs/ai/architecture.md`](ai/architecture.md),
shared conventions in [`docs/ai/conventions.md`](ai/conventions.md), and
fundamental decisions in this file. Application-specific structure is documented
in `frontend/README.md` and `backend/README.md`.

**Consequences.**

- Structural changes update the relevant document in the same change.
- Documents link to each other instead of restating rules.
- Unresolved choices are marked **PENDING** rather than assumed.
