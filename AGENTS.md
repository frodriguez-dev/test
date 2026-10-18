# AGENTS.md

Instructions for AI coding agents working in this repository.

This file is the single source of truth for how agents should behave here. It
is intentionally short, concrete, and verifiable.

## Repository purpose

This is a sandbox for AI-assisted development. It contains small example
implementations (`calculator.py`, `experiments/csv_analyzer`,
`experiments/task_manager`) and a provider-independent foundation for agent
instructions, skills, and documentation.

## Before changing anything

1. Inspect the repository first: read `README.md`, this file, and `docs/ai/`.
2. Read the code and tests around the area you intend to change.
3. Confirm the change is in scope. If a requirement is ambiguous, ask instead
   of guessing.
4. Prefer small, focused changes over broad rewrites.

## Principles

- **Simplicity first.** Solve the stated problem with the least code needed.
- **Maintainability.** Prefer clear names, small functions, and standard
  library solutions.
- **No unnecessary dependencies.** Do not add a dependency without an explicit
  reason.
- **Consistency.** Follow the style of the code you are editing.
- **Reversibility.** Keep changes easy to review and revert.

## Implementation conventions

- Python code targets 3.10+ (see `pyproject.toml`).
- Follow PEP 8 and add type hints where they improve clarity.
- Keep documentation and code comments in English.
- Do not commit generated files (`__pycache__/`, `*.egg-info/`,
  `.pytest_cache/`, runtime artifacts such as `tasks.json`). See `.gitignore`.
- Use only the Python standard library unless a dependency is justified by the
  task.

## Running tests and validating changes

Run the checks relevant to what you changed and report the results.

- Root suite: `python -m pytest`
- CSV analyzer: `python -m unittest discover -s experiments/csv_analyzer/tests -t .`
- Task manager: `python -m unittest discover -s experiments/task_manager/tests -v`

Do not claim a change works without running the applicable tests.

## Destructive operations

Never, without explicit user confirmation:

- Rewrite or delete Git history.
- Force-push or reset shared branches.
- Delete files or branches you did not create and that are not clearly
  obsolete.
- Remove functional GitHub configuration.

When in doubt, stop and ask.

## Before delivering a task

- The change matches the request and stays in scope.
- Applicable tests pass.
- Documentation is updated when behavior or structure changes.
- No obsolete or generated files were added.
- The diff is small enough to review comfortably.

## Commits and Pull Requests

- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`,
  `test:`.
- Write commit messages in English, in the imperative mood, with a concise
  subject.
- Keep one logical change per commit.
- Reference the related issue in the commit body or the Pull Request.
- Pull Requests summarize: what changed, files added or removed, decisions
  taken, and open questions.

## Skills

- Reusable skills live in `.agents/skills/`.
- Discover them by listing `.agents/skills/`; each skill directory contains a
  `SKILL.md`.
- Start new skills from `.agents/skills/_template/SKILL.md`.
- See `.agents/skills/README.md` for organization guidelines.

## Pending decisions

When an architectural or tooling decision is not yet made, record it as
*PENDING* in `docs/ai/` instead of assuming an answer. Current open items are
listed in `docs/ai/architecture.md` and `docs/ai/tooling.md`.
