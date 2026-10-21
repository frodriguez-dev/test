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

- **Status:** Accepted, initialized in issue #18
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
- Exact versions and scripts are recorded in `frontend/package.json`; `@/*` is
  the import alias for `frontend/src/`.

## 0003 — Django, DRF, PostgreSQL, and uv for the backend

- **Status:** Accepted, initialized (Django and PostgreSQL in issue #19; DRF and the API surface in issue #17)
- **Date:** 2026-10-19
- **Issue:** #16

**Context.** The backend must expose a JSON API, model relational data, and stay
simple to operate and test.

**Decision.** Use Django with Django REST Framework for the API, PostgreSQL as
the only database, and uv for dependency and environment management.

**Consequences.**

- Domain state is modeled with Django apps and migrations.
- The API is REST/JSON; GraphQL and a separate ORM layer are out of scope.
- `pyproject.toml` and `uv.lock` live in `backend/` and are managed with uv. The
  root `pyproject.toml` is provisional leftover metadata; renaming or removing it
  is tracked as **PENDING** in [`docs/ai/architecture.md`](ai/architecture.md).
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
- API documentation uses the OpenAPI schema generated from the backend
  (decision 0009).

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

## 0008 — Tailwind CSS and shadcn/ui as the visual system

- **Status:** Accepted, initialized in issue #20
- **Date:** 2026-10-19
- **Issue:** #20

**Context.** The frontend needs a styling approach and a component baseline that
stays close to the platform and can evolve without a bespoke design system.

**Decision.** Use Tailwind CSS v4 through the official Vite plugin for styling,
and shadcn/ui components installed and updated with its official CLI. Component
source lives under `src/components/ui/`, theme tokens in
`src/styles/global.css`, and the CLI configuration in `frontend/components.json`.

**Consequences.**

- UI is built with utility classes and the generated shadcn/ui components.
- shadcn/ui components and their primitives are vendored source, not a runtime
  UI framework; they can be updated with the CLI.
- A custom design system and additional UI libraries remain out of scope until a
  later decision.
- Adding or updating a component requires running the shadcn CLI and committing
  the generated files together with `components.json`.

## 0009 — OpenAPI schema as the API contract

- **Status:** Accepted, initialized in issue #22
- **Date:** 2026-10-19
- **Issue:** #22

**Context.** Frontend and backend are separate applications. Decision 0005
established a versioned REST API but left the documentation format **PENDING**.
Manual API documentation drifts from the implementation and duplicates
information.

**Decision.** Generate the OpenAPI 3 schema from the Django REST Framework code
with drf-spectacular. Expose it at `/api/schema/` and a Swagger UI at
`/api/docs/`. Commit a generated snapshot at `docs/api/openapi.yaml` for review
and consumption, and treat the backend code as the source of truth.

**Consequences.**

- Endpoint documentation is expressed with serializers and
  `extend_schema`; hand-written API references are not maintained.
- `docs/api/openapi.yaml` must be regenerated with
  `uv run manage.py spectacular --file ../docs/api/openapi.yaml` whenever the API
  surface changes. Tests fail when the snapshot is stale or invalid.
- The version in `SPECTACULAR_SETTINGS` tracks the API contract, not the
  application release.
- Schema generation runs offline and adds no runtime service.

## 0010 — Typed frontend API client generated from the OpenAPI contract

- **Status:** Accepted, initialized in issue #23
- **Date:** 2026-10-21
- **Issue:** #23

**Context.** The frontend needs to call the backend without hand-copying request
and response shapes, and without scattering `fetch` calls across components.
Decision 0009 made the OpenAPI document the API contract.

**Decision.** Generate TypeScript types from `docs/api/openapi.yaml` into
`frontend/src/types/api/` with `openapi-typescript-codegen`. Perform all HTTP
access through a single client in `frontend/src/api/` and expose typed endpoint
functions from there. During development, the Vite dev server proxies `/api` to
Django.

**Consequences.**

- API types are regenerated rather than maintained by hand; the committed
  contract and `pnpm generate:api` keep them in sync.
- UI components consume hooks and endpoint functions, so they stay independent
  of HTTP details and easy to test.
- The frontend uses relative `/api` URLs; the dev proxy and the production
  reverse proxy own origin routing. CORS remains unnecessary for the default
  development setup.

## 0011 — Django session authentication for the API

- **Status:** Accepted, implemented in issue #24
- **Date:** 2026-10-21
- **Issue:** #24

**Context.** The application needs a reusable way to sign users in and protect
API operations without introducing a separate token authority. Django already
ships users, sessions, and CSRF protection.

**Decision.** Authenticate the API with Django session authentication and
Django's built-in user system. Expose `csrf`, `login`, `logout`, and `me`
endpoints under `/api/v1/auth/`; keep the session in Django's `HttpOnly` session
cookie and require the CSRF token on unsafe requests. Provide the login screen
and protected routes with React Router.

**Consequences.**

- No JWT, no tokens in `localStorage`, and no public registration, OAuth, or
  role model; users are managed through Django's user system.
- The frontend calls `GET /api/v1/auth/csrf/` to obtain a token and sends it in
  the `X-CSRFToken` header on unsafe requests, including login.
- Session and CSRF cookies use `SameSite=Lax`, are `HttpOnly` where applicable,
  and are marked `Secure` when `DJANGO_DEBUG` is disabled.
- Authentication state is server-authoritative: the frontend loads the current
  user from `/api/v1/auth/me/` instead of decoding a token.
- Cross-origin deployments need a same-site or proxy setup; the default
  development proxy remains the supported path.

## 0012 — Root Makefile for development commands

- **Status:** Accepted, implemented in issue #37
- **Date:** 2026-10-21
- **Issue:** #37

**Context.** The Docker Compose workflow and the local uv and pnpm workflows were
documented in several files, so newcomers and agents had to remember commands
from different places. Decision 0001 kept a root-level task runner out until a
concrete need appeared; the need is now the repeated startup, shell, and test
commands.

**Decision.** Add a root `Makefile` that centralizes the common development
commands and delegates to Docker Compose, uv, and pnpm. Document the full local
development workflow in `DEPLOYING.md`, link it from `README.md`, and expose the
available targets through `make help`.

**Consequences.**

- The `Makefile` contains no application logic and does not replace
  `compose.yaml`, the Dockerfiles, or the application manifests; it only invokes
  them with configurable defaults.
- Ports, service names, and Compose settings can be overridden on the command
  line without editing files.
- Linting, formatting, and new tooling are not invented in the `Makefile`; they
  remain defined by the tools and documented commands until a target is added
  deliberately.
- `DEPLOYING.md` describes local development only, not a production deployment.
