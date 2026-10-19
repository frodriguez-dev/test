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

- Instructions for agents live in `AGENTS.md`.
- Foundation documentation lives under `docs/ai/`.
- Reusable agent skills live under `.agents/skills/<name>/`.

Do not create empty directories or files without a documented purpose.

## Tests

- No test framework is configured yet; selecting one is **PENDING** (see
  [`docs/ai/tooling.md`](tooling.md)).
- Once a framework is adopted, every behavior change must keep the applicable
  test suites passing, and tests must be added or updated alongside behavior
  changes.

## Generated files

Do not commit generated or runtime files. The following are ignored via
`.gitignore` and must stay untracked:

- `__pycache__/` and `*.py[cod]`
- `*.egg-info/`
- `.pytest_cache/`

## Git workflow

- Branch from the main branch using a descriptive name, for example
  `chore/<summary>` or `feature/<summary>`.
- Use Conventional Commit prefixes: `feat:`, `fix:`, `docs:`, `chore:`,
  `refactor:`, `test:`.
- Keep commits focused: one logical change each.
- Reference the related issue in the commit body or Pull Request.
- Never rewrite shared history or force-push shared branches without explicit
  confirmation.

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
