# Development conventions

Shared conventions for humans and AI agents working in this repository. These
apply on top of the general rules in [`AGENTS.md`](../../AGENTS.md).

## Language

- Write documentation, code comments, commit messages, and Pull Request
  descriptions in **English**.
- Keep identifiers in English and descriptive.

## Python

- Target Python 3.10 or higher, as declared in `pyproject.toml`.
- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Add type hints where they improve clarity; avoid redundant annotations.
- Prefer small, single-purpose functions and clear names.
- Rely on the standard library. Justify any new dependency in the task and add
  it to `pyproject.toml` with a reason.

## Repository layout

- Application code lives in `frontend/` and `backend/`; each application owns its
  manifest, lock file, and tests.
- Shared documentation and architecture decisions live in `docs/`; agent
  instructions live in `AGENTS.md`; reusable agent skills live under
  `.agents/skills/<name>/`.
- Issue and Pull Request templates live in `.github/`.
- The root `Makefile` and `DEPLOYING.md` describe the supported local
  development commands; they delegate to Docker Compose, uv, and pnpm.
- Structure and conventions for each application are documented in
  [`frontend/README.md`](../../frontend/README.md) and
  [`backend/README.md`](../../backend/README.md).

Do not create empty directories or files without a documented purpose.

## Code location and dependencies

- Put code next to the concern it serves, not in generic `utils` or `misc`
  modules. Extract shared code only after a second real use appears.
- Keep dependency direction one-way: `frontend → backend → PostgreSQL`. The
  frontend never imports backend files, and the backend never imports frontend
  files.
- Frontend: `src/api/` is the only HTTP boundary; `pages` compose `features`,
  which compose shared `components` and `lib`.
- Backend: one Django app per business domain under `backend/apps/`; keep
  `config/` limited to project wiring.
- Declare every dependency in the application's manifest (`frontend/package.json`
  with pnpm, `backend/pyproject.toml` with uv) and commit its lock file. Do not
  add a dependency without a stated reason or duplicate one already available.
- Configuration comes from environment variables; commit `.env.example` files
  only, never real secrets.

## Frontend

- Target TypeScript with strict mode and keep identifiers descriptive.
- Name files by their primary export and colocate feature-specific components,
  hooks, and tests with their feature.
- Use pnpm; do not introduce a second Node package manager.
- `src/types/api/` is generated from `docs/api/openapi.yaml` with
  `pnpm generate:api`; do not edit it by hand.
- See [`frontend/README.md`](../../frontend/README.md) for the intended
  structure.

## Backend

- Follow the Django conventions implied by the framework: thin views, explicit
  URL routing, migrations committed with model changes, and tests under each
  app's `tests/` directory.
- Keep business rules out of `config/`; it is project wiring only.
- Use PostgreSQL in every environment, including local development.
- See [`backend/README.md`](../../backend/README.md) for the intended structure.

## Tests

- The backend uses pytest with pytest-django; tests live under each app's
  `tests/` directory. Run the suite from `backend/`:

  ```sh
  uv run --env-file .env pytest
  uv run ruff check .
  uv run ruff format --check .
  ```

  The tests use PostgreSQL and create a test database, so the configured role
  needs permission to create databases. Inside Docker Compose, use
  `docker compose exec backend uv run --no-sync pytest`. From the repository
  root, `make backend-test` runs the same suite.

- The frontend uses Vitest with React Testing Library; tests are colocated with
  the code they cover (`*.test.ts` or `*.test.tsx`). Run every frontend check
  from `frontend/`:

  ```sh
  pnpm check   # typecheck, lint, format check, and tests
  ```

  Individual commands are `pnpm typecheck`, `pnpm lint`, `pnpm format:check`,
  and `pnpm test`.

- The OpenAPI contract is generated from the backend. When the API surface
  changes, regenerate the snapshot and the frontend types, then rerun the
  affected checks:

  ```sh
  # from backend/
  uv run --env-file .env manage.py spectacular --file ../docs/api/openapi.yaml
  # from frontend/
  pnpm generate:api
  ```

  `docs/api/openapi.yaml` is committed; do not edit it by hand.

- Every behavior change must keep the applicable test suites passing, and tests
  must be added or updated alongside behavior changes.
- A documentation-only change does not need runtime tests, but must be reviewed
  for valid links and formatting; `git diff --check` catches whitespace errors.

## Generated files

Do not commit generated or runtime files. The following are ignored via
`.gitignore` and must stay untracked:

- Python: `__pycache__/`, `*.py[cod]`, `*.egg-info/`, `.venv/`, `.pytest_cache/`
- Node: `node_modules/`, `dist/`, `coverage/`
- Environment and secrets: `.env`, `.env.*` (except `.env.example`)
- Local runtime data: `backend/media/`, `backend/staticfiles/`

## Git workflow

- Branch from the main branch using a descriptive name, for example
  `feature/<summary>`, `fix/<summary>`, or `chore/<summary>`. Keep an
  Orca-generated `<account>/<summary>` branch as created instead of renaming
  another agent's branch.
- Use Conventional Commit prefixes: `feat:`, `fix:`, `docs:`, `chore:`,
  `refactor:`, `test:`.
- Keep commits focused: one logical change each.
- Reference the related issue in the commit body or Pull Request.
- Never rewrite shared history or force-push shared branches without explicit
  confirmation.

## Issues and Pull Requests

- Use the templates in `.github/`: `ISSUE_TEMPLATE/task.md` and
  `pull_request_template.md`.
- One issue per branch and Pull Request. Do not mix unrelated changes.
- Write Pull Request descriptions in English and include the summary, related
  issue, validation commands and results, and known risks.
- Verify GitHub authentication with `gh auth status` before pushing or opening a
  Pull Request. See [`orca.md`](orca.md#prerequisites-and-authentication) for
  the full workflow.
- Agents may open or update a Pull Request when authorized, but must not merge,
  approve, close, or enable auto-merge on it. Merging is a human decision.
- Respond to review feedback on the same branch and Pull Request; do not open a
  duplicate Pull Request.

## Documentation

- Update documentation when structure, behavior, or conventions change.
- Prefer links over duplication; see
  [`docs/ai/architecture.md`](architecture.md).
- Mark unresolved choices as **PENDING** instead of presenting them as decided.

## Skills

- Create a skill only when its purpose is clear; see
  [`.agents/skills/README.md`](../../.agents/skills/README.md).
- Start from `.agents/skills/_template/SKILL.md`.
- Keep skills focused; split them when they cover unrelated concerns.
- Treat third-party skills as untrusted until reviewed. Record provenance,
  license, and validation status in [`docs/ai/skills.md`](skills.md).
- Keep installed skills project-scoped and commit the skill files, relative
  `.claude/skills` links, and `skills-lock.json` together.
