# AI-Assisted Development Foundation

This repository is a clean, provider-independent foundation for **software
development assisted by AI agents**. It provides shared instructions, a skills
system, and architecture documentation that humans and agents can both follow
and build on. It is also the monorepo for the React and Django applications
described below.

## Stack

The backend uses Django, Django REST Framework, PostgreSQL, and uv; the frontend
uses React, TypeScript, Vite, and pnpm. Issue #16 established the structure,
issue #18 added the frontend toolchain, issue #19 initialized the backend, issue
#17 added Django REST Framework and the first endpoint (`GET /api/health/`),
issue #21 added the Docker Compose development environment, issue #22 added the
generated OpenAPI contract and its documentation endpoints, issue #23 connected
the frontend to the API with a typed HTTP client, and issue #24 added session
authentication with a login screen and protected routes. Issue #25 added Ruff,
pytest, ESLint, Prettier, Vitest, and React Testing Library. Issue #37 added the
root `Makefile` and [`DEPLOYING.md`](DEPLOYING.md). Issue #27 documented the Orca
and GitHub issue workflow. Issue #44 added the local quality gate, Mypy, and the
complexity and security checks.

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
├── REVIEW.md            # Canonical code review policy
├── README.md            # This file
├── DEPLOYING.md         # Step-by-step local development guide
├── Makefile             # Development commands for Docker, local toolchains, and quality
├── pytest.ini           # Root pytest entry point for the tooling tests
├── THIRD_PARTY_NOTICES.md  # Licenses for vendored skills
├── skills-lock.json     # Agent Skills installer lock file
├── compose.yaml         # Development environment: frontend, backend, and db
├── pyproject.toml       # Provisional root Python metadata (moves to backend/)
├── .agents/
│   └── skills/          # Installed skills, template, and catalog
├── .claude/
│   └── skills/          # Relative links to the canonical skills
├── .github/             # Issue and Pull Request templates
├── backend/             # Django REST API (Django + DRF + PostgreSQL initialized)
│   ├── Dockerfile       # Development image
│   └── README.md        # Backend structure, setup, and boundaries
├── frontend/            # React SPA (initialized: React, TypeScript, Vite, pnpm)
│   ├── Dockerfile       # Development image
│   └── README.md        # Frontend structure, commands, and boundaries
├── tools/
│   └── agent_pipeline/  # Repository tooling; owns the local quality gate
└── docs/
    ├── decisions.md     # Fundamental architecture decisions
    ├── api/
    │   └── openapi.yaml # Generated OpenAPI contract snapshot
    └── ai/              # Architecture, conventions, workflow, tooling, and skills notes
```

## Getting started

Read the foundation in this order:

1. [`AGENTS.md`](AGENTS.md) — how agents should work in this repository.
2. [`REVIEW.md`](REVIEW.md) — code review standards, severity, and approval.
3. [`docs/ai/orca.md`](docs/ai/orca.md) — the issue-to-pull-request workflow
   with Orca and GitHub.
4. [`docs/ai/architecture.md`](docs/ai/architecture.md) — how the application
   layers and the AI foundation fit together.
5. [`docs/decisions.md`](docs/decisions.md) — why the stack and boundaries were
   chosen.
6. [`docs/ai/conventions.md`](docs/ai/conventions.md) — coding, repository, and
   dependency conventions.
7. [`docs/ai/tooling.md`](docs/ai/tooling.md) — tools that are used, proposed,
   or still being evaluated.
8. [`docs/ai/skills.md`](docs/ai/skills.md) — installed Agent Skills,
   provenance, and maintenance.
9. [`.agents/skills/`](.agents/skills/README.md) — reusable agent skills.
10. [`DEPLOYING.md`](DEPLOYING.md) — how to start and verify the development
    environment.

## Local development with Docker Compose

Requires Docker Engine with the Compose plugin and GNU Make. The configuration
targets local development only; it is not a production deployment. For a
complete step-by-step guide, including the non-Docker workflow and
troubleshooting, see [`DEPLOYING.md`](DEPLOYING.md). `make help` lists every
target.

```sh
make up-build     # build images and start db, backend, frontend in background
make up           # start existing images without rebuilding
make logs         # follow service logs
make status       # show service status
make down         # stop the services, keep database data
make down-volumes # stop the services and delete database data (destructive)
```

The services are available at:

| Service  | Address                 | Notes                                                                                                                 |
| -------- | ----------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Frontend | <http://localhost:5173> | Vite dev server with hot module replacement.                                                                          |
| Backend  | <http://localhost:8000> | Django dev server; `GET /api/health/` reports `{"status": "ok"}`. API docs at `/api/docs/`, schema at `/api/schema/`. |
| Database | `db:5432`               | PostgreSQL, reachable only from the other Compose services.                                                           |

`make health` checks `GET /api/health/` from the host. Source directories are
bind-mounted, so frontend and backend reload on change.
The backend applies migrations on startup and waits for the PostgreSQL
healthcheck before starting. PostgreSQL data lives in the named volume
`postgres_data`; `make down` keeps it and `make down-volumes` removes it.

The credentials in `compose.yaml` are non-secret development defaults. Override
them with shell environment variables or a local root `.env` file (for example
`POSTGRES_PASSWORD`, `DJANGO_SECRET_KEY`, `BACKEND_PORT`, or `FRONTEND_PORT`).
Never commit real credentials. The `.env` file is ignored by Git.

For the non-Docker setup, follow [`DEPLOYING.md`](DEPLOYING.md) or see
[`backend/README.md`](backend/README.md) and
[`frontend/README.md`](frontend/README.md).

## Quality checks

`make quality` runs every required backend, frontend, complexity, and security
check through the repository-level tooling package in
[`tools/agent_pipeline/`](tools/agent_pipeline/README.md). It prints a summary,
writes `.quality/quality.json` (`schema_version = 1`), and keeps capped per-check
logs in `.quality/logs/`. Both are ignored by Git. The command is local only; it
does not use GitHub Actions or a hosted runner.

```sh
make quality                         # every required check
make quality-backend                 # backend checks only
make quality-frontend                # frontend checks only
make quality-complexity              # C901 and ESLint complexity only
make quality-security                # security checks; network checks stay opt-in
make quality-tests                   # tests for the quality-gate tooling
make quality QUALITY_ARGS="--json --output /tmp/quality.json"
make quality QUALITY_ARGS="--security-network"
```

The gate requires PostgreSQL and `backend/.env` (copy `.env.example`), backend
dependencies from `uv sync`, and frontend dependencies from `pnpm install`.
`backend-test` and `frontend-build` reuse the existing Make targets; the other
checks use the documented Ruff, Mypy, and pnpm commands.

| Exit | Gate status | Meaning                                                                    |
| ---- | ----------- | -------------------------------------------------------------------------- |
| `0`  | `PASS`      | Every required check passed.                                               |
| `1`  | `FAIL`      | At least one required check failed.                                        |
| `2`  | `ERROR`     | A required check was skipped, timed out, or could not start; or the config is invalid. |

GNU Make reports `2` for any failed recipe, so the exact `1` versus `2` code is
available from the direct CLI command and in `.quality/quality.json`. On a clean
run `make quality` exits `0`.

A missing tool or timeout is never reported as `PASS`. Network-dependent
`uv audit` and `pnpm audit` are optional and report `SKIP` unless
`--security-network` is passed. Ruff `S` runs offline and is required.

Thresholds, timeouts, and the security opt-in live in
[`tools/agent_pipeline/pyproject.toml`](tools/agent_pipeline/pyproject.toml);
unknown keys are rejected. The complexity baseline is 10 for both Python (Ruff
`C901`) and TypeScript (ESLint core `complexity`). Mypy type checking is required
for the backend. See [`docs/ai/conventions.md`](docs/ai/conventions.md#tests) for
the per-layer commands and [`docs/ai/tooling.md`](docs/ai/tooling.md) for the
security decisions.

To run a single layer directly:

```sh
# Backend (from backend/); requires PostgreSQL
uv run --env-file .env pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy manage.py config apps

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
error states, and protects an example route behind a login screen. Ruff, Mypy,
and pytest cover the backend; ESLint, Prettier, Vitest, and React Testing Library
cover the frontend. `make quality` runs the full local gate and writes a stable
JSON result. `make up-build` starts the complete development stack. Unresolved
choices are tracked as _PENDING_ in the `docs/ai/` documents rather than assumed.
A first set of professional Agent Skills is installed and versioned in the
repository; see [`docs/ai/skills.md`](docs/ai/skills.md). Issue and Pull Request
templates live in `.github/`, the Orca-based issue workflow is documented in
[`docs/ai/orca.md`](docs/ai/orca.md), and the canonical review policy is
[`REVIEW.md`](REVIEW.md).
