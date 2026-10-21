# AI-Assisted Development Foundation

This repository is a clean, provider-independent foundation for **software
development assisted by AI agents**. It provides shared instructions, a skills
system, and architecture documentation that humans and agents can both follow
and build on. It is also the monorepo for the React and Django applications
described below.

## Planned stack

The backend is initialized with Django, Django REST Framework, PostgreSQL, and
uv; the frontend is initialized with React, TypeScript, Vite, and pnpm. Issue #16
established the structure, issue #18 added the frontend toolchain, issue #19
initialized the backend, issue #17 added Django REST Framework and the first
endpoint (`GET /api/health/`), issue #21 added the Docker Compose
development environment, issue #22 added the generated OpenAPI contract and
its documentation endpoints, issue #23 connected the frontend to the API
with a typed HTTP client, and issue #24 added session authentication with a
login screen and protected routes. Issue #25 added Ruff, pytest, ESLint,
Prettier, Vitest, and React Testing Library.

| Layer    | Stack                                                | Location                     |
| -------- | ---------------------------------------------------- | ---------------------------- |
| Frontend | React, TypeScript, Vite, pnpm                        | `frontend/`                  |
| Backend  | Django, Django REST Framework, uv                    | `backend/`                   |
| Database | PostgreSQL                                           | Accessed by the backend only |
| API      | REST/JSON under `/api/v1/` (plus `GET /api/health/`) | `backend/`                   |

## Purpose

- Establish a clear, minimal base for AI-assisted development.
- Keep instructions, skills, and tooling consistent and free of duplication.
- Stay independent of any specific agent, model, or vendor.
- Keep frontend, backend, and documentation in one repository with explicit
  boundaries.

## Repository layout

```
.
├── AGENTS.md            # Instructions for AI coding agents
├── README.md            # This file
├── THIRD_PARTY_NOTICES.md  # Licenses for vendored skills
├── skills-lock.json     # Agent Skills installer lock file
├── compose.yaml         # Development environment: frontend, backend, and db
├── pyproject.toml       # Provisional root Python metadata (moves to backend/)
├── .agents/
│   └── skills/          # Installed skills, template, and catalog
├── .claude/
│   └── skills/          # Relative links to the canonical skills
├── backend/             # Django REST API (Django + DRF + PostgreSQL initialized)
│   ├── Dockerfile       # Development image
│   └── README.md        # Backend structure, setup, and boundaries
├── frontend/            # React SPA (initialized: React, TypeScript, Vite, pnpm)
│   ├── Dockerfile       # Development image
│   └── README.md        # Frontend structure, commands, and boundaries
└── docs/
    ├── decisions.md     # Fundamental architecture decisions
    ├── api/
    │   └── openapi.yaml # Generated OpenAPI contract snapshot
    └── ai/              # Architecture, conventions, tooling, and skills notes
```

## Getting started

Read the foundation in this order:

1. [`AGENTS.md`](AGENTS.md) — how agents should work in this repository.
2. [`docs/ai/architecture.md`](docs/ai/architecture.md) — how the application
   layers and the AI foundation fit together.
3. [`docs/decisions.md`](docs/decisions.md) — why the stack and boundaries were
   chosen.
4. [`docs/ai/conventions.md`](docs/ai/conventions.md) — coding, repository, and
   dependency conventions.
5. [`docs/ai/tooling.md`](docs/ai/tooling.md) — tools that are used, proposed,
   or still being evaluated.
6. [`docs/ai/skills.md`](docs/ai/skills.md) — installed Agent Skills,
   provenance, and maintenance.
7. [`.agents/skills/`](.agents/skills/README.md) — reusable agent skills.

## Local development with Docker Compose

Requires Docker Engine with the Compose plugin. The configuration targets local
development only; it is not a production deployment.

```sh
docker compose up --build        # build images and start db, backend, frontend
docker compose up -d --build     # same, in the background
docker compose logs -f           # follow service logs
docker compose down              # stop the services, keep database data
docker compose down -v           # stop the services and delete database data
```

The services are available at:

| Service  | Address                 | Notes                                                                                                                 |
| -------- | ----------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Frontend | <http://localhost:5173> | Vite dev server with hot module replacement.                                                                          |
| Backend  | <http://localhost:8000> | Django dev server; `GET /api/health/` reports `{"status": "ok"}`. API docs at `/api/docs/`, schema at `/api/schema/`. |
| Database | `db:5432`               | PostgreSQL, reachable only from the other Compose services.                                                           |

Source directories are bind-mounted, so frontend and backend reload on change.
The backend applies migrations on startup and waits for the PostgreSQL
healthcheck before starting. PostgreSQL data lives in the named volume
`postgres_data`; `docker compose down` keeps it and `docker compose down -v`
removes it.

The credentials in `compose.yaml` are non-secret development defaults. Override
them with shell environment variables or a local root `.env` file (for example
`POSTGRES_PASSWORD`, `DJANGO_SECRET_KEY`, `BACKEND_PORT`, or `FRONTEND_PORT`).
Never commit real credentials. The `.env` file is ignored by Git.

For the non-Docker setup, see [`backend/README.md`](backend/README.md) and
[`frontend/README.md`](frontend/README.md).

## Quality checks

Run the checks for the layer you changed:

```sh
# Backend (from backend/); requires PostgreSQL
uv run --env-file .env pytest
uv run ruff check .
uv run ruff format --check .

# Frontend (from frontend/)
pnpm check   # typecheck, lint, format check, and tests
```

The backend tests create a test database. With Docker Compose running, use
`docker compose exec backend uv run --no-sync pytest` instead. See
[`docs/ai/conventions.md`](docs/ai/conventions.md#tests) for details.

## Status

This is an early foundation. The monorepo structure is defined and the backend
(Django, Django REST Framework, and PostgreSQL) and frontend (React, TypeScript,
Vite, and pnpm) toolchains are initialized. The backend exposes the
infrastructure endpoint `GET /api/health/`, the generated OpenAPI contract at
`/api/schema/` and `/api/docs/`, and session authentication endpoints under
`/api/v1/auth/`. The frontend calls the API through a centralized HTTP client
with generated TypeScript types, shows the health check's loading, success, and
error states, and protects an example route behind a login screen. Ruff and
pytest cover the backend; ESLint, Prettier, Vitest, and React Testing Library
cover the frontend.
`docker compose up --build` starts the complete development stack. Unresolved
choices are tracked as _PENDING_ in the `docs/ai/` documents rather than assumed.
A first set of professional Agent Skills is installed and versioned in the
repository; see [`docs/ai/skills.md`](docs/ai/skills.md).
