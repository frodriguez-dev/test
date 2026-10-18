# Tooling catalog

Tools that are used, proposed, or still being evaluated for AI-assisted
development in this repository.

**No external service is installed or configured as part of this foundation.**
The catalog records candidates and decisions; adoption happens in later tasks.

## Status legend

- **In use** — currently relied upon in this repository.
- **Proposed** — recommended for adoption; not yet installed or configured.
- **Pending evaluation** — candidate that needs a decision before adoption.

## Agents and coding assistants

| Tool | Status | Notes |
| --- | --- | --- |
| AI coding agents (provider-independent) | In use | Governed by [`AGENTS.md`](../../AGENTS.md); no single vendor is assumed. |
| Additional coding agents | Pending evaluation | Which agents to standardize on is **PENDING**. |

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
| `pytest` | In use | Root test suite (`python -m pytest`). |
| `unittest` | In use | Test suites for the `experiments/` applications. |
| Coverage measurement | Pending evaluation | Not configured. |

## Static analysis and code quality

| Tool | Status | Notes |
| --- | --- | --- |
| Linter / formatter | Proposed | Ruff is a candidate; not yet adopted. |
| Type checker | Proposed | Mypy is a candidate; not yet adopted. |
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
