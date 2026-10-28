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
| GNU Make                   | In use | Root `Makefile` wraps the Docker Compose, uv, pnpm, and quality-gate commands (issues #37 and #44).                                             |
| agent_pipeline             | In use | Repository tooling at `tools/agent_pipeline/`; owns the local quality gate (issue #44). Python 3.11+, standard library only.                     |

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

| Tool                 | Status             | Notes                                                                                                                |
| -------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------- |
| Backend test runner  | In use             | pytest with pytest-django; configured in `backend/pyproject.toml` (issue #25).                                       |
| Frontend test runner | In use             | Vitest with React Testing Library and jsdom; configured in `vite.config.ts` (issue #25).                             |
| Quality gate         | In use             | `make quality` / `agent_pipeline quality`; 14 checks, JSON schema version 1 (issue #44). See below.                  |
| Tooling tests        | In use             | pytest for `tools/agent_pipeline/`; `uv run --project tools/agent_pipeline pytest` (issue #44).                      |
| Coverage measurement | Pending evaluation | Not configured.                                                                                                      |

## Quality gate

The local gate is implemented as a library plus CLI in
`tools/agent_pipeline/agent_pipeline/quality/`, not as a shell script, so later
pipeline issues can call it in-process. It runs:

- Backend: Ruff `check`, Ruff `format --check`, Mypy, and pytest.
- Frontend: `pnpm typecheck`, `lint`, `format:check`, `test`, and `build`.
- Complexity: Ruff `C901` (maximum 10) and the ESLint core `complexity` rule
  (maximum 10).
- Security: Ruff `S` (required) plus the opt-in audits below.

Configuration, thresholds, and timeouts live in
`tools/agent_pipeline/pyproject.toml`; unknown keys are rejected. The tooling
package requires Python 3.11 or newer for `tomllib`; the backend keeps its 3.10
target. Exit codes are `0` for pass, `1` for a required failure, and `2` for a
configuration error, missing tool, timeout, or skipped required check. GNU Make
reports `2` for any failed recipe, so the exact `1`/`2` distinction is visible
when calling the CLI directly or in the JSON report. The JSON report has
`schema_version = 1` and the fields documented in
[`tools/agent_pipeline/README.md`](../../tools/agent_pipeline/README.md).
The gate is deliberately local: it adds no GitHub Actions workflow and does not
depend on issue #26's hosted CI.

## Static analysis and code quality

| Tool              | Status   | Notes                                                                                                                                                                                  |
| ----------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ruff              | In use   | Python linter and formatter for `backend/`; configured in `backend/pyproject.toml`. Selects `C90` (mccabe max 10) and `S` in addition to the base rules (issues #25 and #44).         |
| Mypy              | In use   | Python type checker for `backend/`; required by the quality gate. Third-party stubs for Django, DRF, drf-spectacular, and PyYAML are not adopted yet, so those imports are ignored.     |
| ESLint + Prettier | In use   | Frontend linting and formatting; configured through `frontend/eslint.config.js` and `frontend/.prettierrc.json`. The core `complexity` rule is enabled at 10 (issues #25 and #44).     |
| Pre-commit hooks  | Pending evaluation | Would wire linters to Git; decided after linters.                                                                                                                                     |

## Security decisions

The quality gate evaluates the checks available without adding a platform or a
hosted runner (issue #44):

| Check                        | Decision | Rationale and behavior                                                                                                                              |
| ---------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ruff `S` (bandit rules)      | Adopt    | Offline and already part of Ruff. Required in the gate; only test-only `S105`/`S106` fixtures are ignored in `backend/pyproject.toml`.               |
| `uv audit`                   | Adopt    | High signal for vulnerable Python dependencies. Network-dependent, so it is opt-in (`--security-network`) and reports `SKIP` by default, never `PASS`. |
| `pnpm audit`                 | Adopt    | Built into pnpm and high signal for Node dependencies. Network-dependent, so it is opt-in and reports `SKIP` by default, never `PASS`. Failures stay advisory (optional check) until the existing transitive advisories are updated separately. |
| Secret scanning              | Defer    | No offline, existing repository option. Adding gitleaks or a hosted platform is out of scope until issue #26 or a dedicated task justifies it.       |
| gitleaks, Trivy, pip-audit   | Not adopted | Redundant with the checks above, or require a new dependency/platform not justified by a concrete gap.                                                |

## Security and permissions

| Tool                        | Status             | Notes                                                                                          |
| --------------------------- | ------------------ | ---------------------------------------------------------------------------------------------- |
| Permission and safety rules | In use             | Documented in [`AGENTS.md`](../../AGENTS.md) (destructive operations section).                  |
| Ruff `S` security rules     | In use             | Required offline check in the quality gate (issue #44).                                        |
| `uv audit` / `pnpm audit`   | In use (opt-in)    | Network-dependent, disabled by default; run with `--security-network` (issue #44).             |
| Secret scanning             | Deferred           | No existing offline option; adding a new platform is out of scope for issue #44.               |

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
