# Tooling catalog

Tools that are used, proposed, or still being evaluated for AI-assisted
development in this repository.

**No external service is installed or configured as part of this foundation.**
The catalog records candidates and decisions; adoption happens in later tasks.

## Status legend

- **In use** — currently relied upon in this repository.
- **Proposed** — recommended for adoption; not yet installed or configured.
- **Pending evaluation** — candidate that needs a decision before adoption.

## Application stack

The stack is decided in [`docs/decisions.md`](../decisions.md) and partially
installed. Django, PostgreSQL, and uv are initialized in the backend (issue #19),
and React, TypeScript, Vite, and pnpm are initialized in the frontend (issue
#18). Tailwind CSS and shadcn/ui provide the frontend visual system (issue #20).
Django REST Framework and the API surface (issue #17) are still pending.

| Tool | Status | Notes |
| --- | --- | --- |
| React + TypeScript | In use | Frontend UI and language; initialized in issue #18. |
| Vite | In use | Frontend build and dev server; proxies `/api` during development. |
| pnpm | In use | Frontend package manager; `frontend/pnpm-lock.yaml` is committed. |
| Tailwind CSS | In use | Frontend styling through the `@tailwindcss/vite` plugin; configured in issue #20. |
| shadcn/ui | In use | Frontend component source managed by its CLI; `frontend/components.json` is committed. |
| Django | In use | Backend web framework; project lives under `backend/`. |
| Django REST Framework | Proposed | JSON API under `/api/v1/`; added in issue #17. |
| PostgreSQL | In use | Only database, in every environment including local development. |
| uv | In use | Backend dependency and environment management; `backend/uv.lock` is committed. |

## Agents and coding assistants

| Tool | Status | Notes |
| --- | --- | --- |
| AI coding agents (provider-independent) | In use | Governed by [`AGENTS.md`](../../AGENTS.md); no single vendor is assumed. |
| Codex CLI | In use | Project skills discovery verified with `.agents/skills/`. |
| OpenCode | In use | Project skills discovery verified with `.agents/skills/`. |
| Claude Code | In use | Reads the same skills through relative links in `.claude/skills/`; discovery test pending authentication. |

## Agent skills

| Tool | Status | Notes |
| --- | --- | --- |
| `skills` CLI (`npx skills`) | In use | Version 1.7.2; project-scoped installs; lock file `skills-lock.json`. See [`skills.md`](skills.md). |
| Installed Agent Skills | In use | Five third-party skills, vendored under `.agents/skills/`. |

## Orchestration and autonomous execution

| Tool | Status | Notes |
| --- | --- | --- |
| Orchestration layer | Pending evaluation | Whether one is needed, and which, is **PENDING**. Out of scope for this foundation. |

## MCP tools

| Tool | Status | Notes |
| --- | --- | --- |
| MCP servers | Pending evaluation | Which servers to use and for which capabilities is **PENDING**. |

## Git and GitHub

| Tool | Status | Notes |
| --- | --- | --- |
| Git | In use | Version control; Conventional Commits convention. |
| GitHub (issues, Pull Requests) | In use | Issue-driven workflow; see `AGENTS.md`. |
| GitHub CLI (`gh`) | In use | Reading issues and opening Pull Requests. |

## Testing and validation

| Tool | Status | Notes |
| --- | --- | --- |
| Test framework | Pending evaluation | None configured yet. Intended split: Vitest + React Testing Library for the frontend and `pytest-django` (or Django's runner) for the backend. |
| Coverage measurement | Pending evaluation | Not configured. |

## Static analysis and code quality

| Tool | Status | Notes |
| --- | --- | --- |
| Ruff | Proposed | Python linter and formatter for `backend/`; not yet adopted. |
| Mypy | Proposed | Python type checker for `backend/`; not yet adopted. |
| ESLint + Prettier | Proposed | Frontend linting and formatting; not configured in issue #18, still proposed. |
| Pre-commit hooks | Pending evaluation | Would wire linters to Git; decided after linters. |

## Security and permissions

| Tool | Status | Notes |
| --- | --- | --- |
| Permission and safety rules | In use | Documented in [`AGENTS.md`](../../AGENTS.md) (destructive operations section). |
| Secret scanning | Pending evaluation | Not configured. |

## Documentation and context search

| Tool | Status | Notes |
| --- | --- | --- |
| Markdown documentation | In use | `docs/ai/`, `README.md`, and `AGENTS.md`. |
| Context / code search tooling | Pending evaluation | To be decided alongside MCP adoption. |

## How to add a tool

Follow the "Adding a new tool" process in
[`docs/ai/architecture.md`](architecture.md): choose a category, set an explicit
status, justify it, and integrate it through a thin adapter rather than
duplicating instructions.
