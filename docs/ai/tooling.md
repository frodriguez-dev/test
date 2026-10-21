# Tooling catalog

Tools that are used, proposed, or still being evaluated for AI-assisted
development in this repository.

The repository does not depend on a hosted AI service at build or runtime.
Orca and the GitHub CLI are used for local workspace and Pull Request
operations, and their authentication requirements are documented in
[`orca.md`](orca.md). The catalog records candidates and decisions; adoption
happens in later tasks.

## Status legend

- **In use** — currently relied upon in this repository.
- **Proposed** — recommended for adoption; not yet installed or configured.
- **Pending evaluation** — candidate that needs a decision before adoption.

## Application stack

The stack is decided in [`docs/decisions.md`](../decisions.md). Django, Django
REST Framework, PostgreSQL, and uv are initialized in the backend (issues #19
and #17), and React, TypeScript, Vite, and pnpm are initialized in the frontend
(issue #18). Tailwind CSS and shadcn/ui provide the frontend visual system
(issue #20).

| Tool                       | Status | Notes                                                                                                                                               |
| -------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| React + TypeScript         | In use | Frontend UI and language; initialized in issue #18. TypeScript is pinned to 6.0 because typescript-eslint does not support 7.0 yet.                 |
| React Router               | In use | Client-side routing and the protected-route guard (issue #24).                                                                                      |
| Vite                       | In use | Frontend build and dev server; proxies `/api` during development.                                                                                   |
| pnpm                       | In use | Frontend package manager; `frontend/pnpm-lock.yaml` is committed.                                                                                   |
| Tailwind CSS               | In use | Frontend styling through the `@tailwindcss/vite` plugin; configured in issue #20.                                                                   |
| shadcn/ui                  | In use | Frontend component source managed by its CLI; `frontend/components.json` is committed.                                                              |
| Django                     | In use | Backend web framework; project lives under `backend/`.                                                                                              |
| Django REST Framework      | In use | JSON API under `/api/v1/`; initialized in issue #17 (JSON renderer only).                                                                           |
| drf-spectacular            | In use | Generates the OpenAPI contract exposed at `/api/schema/` and `/api/docs/`; snapshot in `docs/api/openapi.yaml` (issue #22).                         |
| openapi-typescript-codegen | In use | Generates `frontend/src/types/api/` from `docs/api/openapi.yaml` (`pnpm generate:api`); keeps frontend types aligned with the contract (issue #23). |
| PostgreSQL                 | In use | Only database, in every environment including local development.                                                                                    |
| uv                         | In use | Backend dependency and environment management; `backend/uv.lock` is committed.                                                                      |
| Docker                     | In use | Development images in `backend/Dockerfile` and `frontend/Dockerfile`.                                                                               |
| Docker Compose             | In use | `compose.yaml` runs frontend, backend, and PostgreSQL together (issue #21).                                                                         |
| GNU Make                   | In use | Root `Makefile` wraps the Docker Compose, uv, and pnpm development commands (issue #37).                                                              |

## Agents and coding assistants

| Tool                                    | Status | Notes                                                                                                     |
| --------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------- |
| AI coding agents (provider-independent) | In use | Governed by [`AGENTS.md`](../../AGENTS.md); no single vendor is assumed.                                  |
| Orca                                    | In use | Workspaces, worktrees, terminals, and agent sessions; workflow in [`orca.md`](orca.md).                   |
| Codex CLI                               | In use | Project skills discovery verified with `.agents/skills/`.                                                 |
| OpenCode                                | In use | Project skills discovery verified with `.agents/skills/`.                                                 |
| Claude Code                             | In use | Reads the same skills through relative links in `.claude/skills/`; discovery test pending authentication. |

## Agent skills

| Tool                        | Status   | Notes                                                                                               |
| --------------------------- | -------- | --------------------------------------------------------------------------------------------------- |
| `skills` CLI (`npx skills`) | In use   | Version 1.7.2; project-scoped installs; lock file `skills-lock.json`. See [`skills.md`](skills.md). |
| Installed Agent Skills      | In use   | Five third-party skills, vendored under `.agents/skills/`.                                          |
| Proposed stack skills       | Proposed | React, Django, and code-review candidates; not installed. See [`skills.md`](skills.md).             |

## Orchestration and autonomous execution

| Tool                | Status | Notes                                                                                                                       |
| ------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| Orca                | In use | Provides isolated worktrees, terminals, and agent sessions. Replaces the earlier **PENDING** orchestration decision.        |
| Custom orchestrator | Rejected | Not built. Orca covers workspace isolation and agent launch; GitHub Issues and Pull Requests remain the source of truth.     |

## MCP tools

| Tool        | Status             | Notes                                                           |
| ----------- | ------------------ | --------------------------------------------------------------- |
| MCP servers | Pending evaluation | Which servers to use and for which capabilities is **PENDING**. |

## Git and GitHub

| Tool                           | Status | Notes                                                                                             |
| ------------------------------ | ------ | ------------------------------------------------------------------------------------------------- |
| Git                            | In use | Version control; Conventional Commits convention.                                                 |
| GitHub (issues, Pull Requests) | In use | Issue-driven workflow; see [`orca.md`](orca.md).                                                  |
| GitHub CLI (`gh`)              | In use | Reading issues, pushing branches, and opening Pull Requests. Requires an authenticated account.   |
| GitHub authentication          | In use | `gh auth login` plus `gh auth status`; required scope `repo`. Never store tokens in the repository. |
| Issue and PR templates         | In use | `.github/ISSUE_TEMPLATE/task.md` and `.github/pull_request_template.md`.                          |

## Testing and validation

| Tool                 | Status             | Notes                                                                                    |
| -------------------- | ------------------ | ---------------------------------------------------------------------------------------- |
| Backend test runner  | In use             | pytest with pytest-django; configured in `backend/pyproject.toml` (issue #25).           |
| Frontend test runner | In use             | Vitest with React Testing Library and jsdom; configured in `vite.config.ts` (issue #25). |
| Coverage measurement | Pending evaluation | Not configured.                                                                          |

## Static analysis and code quality

| Tool              | Status             | Notes                                                                                                                        |
| ----------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| Ruff              | In use             | Python linter and formatter for `backend/`; configured in `backend/pyproject.toml` (issue #25).                              |
| Mypy              | Proposed           | Python type checker for `backend/`; not yet adopted.                                                                         |
| ESLint + Prettier | In use             | Frontend linting and formatting; configured through `frontend/eslint.config.js` and `frontend/.prettierrc.json` (issue #25). |
| Pre-commit hooks  | Pending evaluation | Would wire linters to Git; decided after linters.                                                                            |

## Security and permissions

| Tool                        | Status             | Notes                                                                          |
| --------------------------- | ------------------ | ------------------------------------------------------------------------------ |
| Permission and safety rules | In use             | Documented in [`AGENTS.md`](../../AGENTS.md) (destructive operations section). |
| Secret scanning             | Pending evaluation | Not configured.                                                                |

## Documentation and context search

| Tool                          | Status             | Notes                                     |
| ----------------------------- | ------------------ | ----------------------------------------- |
| Markdown documentation        | In use             | `docs/ai/`, `README.md`, and `AGENTS.md`. |
| Context / code search tooling | Pending evaluation | To be decided alongside MCP adoption.     |

## How to add a tool

Follow the "Adding a new tool" process in
[`docs/ai/architecture.md`](architecture.md): choose a category, set an explicit
status, justify it, and integrate it through a thin adapter rather than
duplicating instructions.
