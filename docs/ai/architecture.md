# Repository and AI development architecture

This document describes the application architecture of the monorepo and how
the pieces of the AI-assisted development foundation relate to each other, along
with the principles that keep them consistent.

It is a starting point for future decisions, not a final specification.

## Application architecture

The repository is a monorepo with two deployable applications and shared
documentation. The backend uses Django, Django REST Framework, and PostgreSQL;
the frontend uses React, TypeScript, Vite, Tailwind CSS, shadcn/ui, and pnpm.
`compose.yaml` runs the frontend, backend, and PostgreSQL together for local
development, and the root `Makefile` wraps the common Docker Compose, uv, and
pnpm commands. Application structure is defined in
[`frontend/README.md`](../../frontend/README.md) and
[`backend/README.md`](../../backend/README.md), and local setup in
[`DEPLOYING.md`](../../DEPLOYING.md).

| Layer                         | Location                                | Responsibility                                                                                                 | Depends on            |
| ----------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------- |
| Frontend                      | `frontend/`                             | React/TypeScript single-page application: routing, UI, client-side state, and HTTP access to the API.          | Backend REST API only |
| Backend                       | `backend/`                              | Django/DRF application: request handling, validation, business rules, persistence, and the versioned JSON API. | PostgreSQL            |
| Data                          | PostgreSQL                              | Durable relational storage and constraints.                                                                    | —                     |
| Documentation and AI guidance | `docs/`, `AGENTS.md`, `REVIEW.md`, `.agents/skills/`, `.github/` | Architecture, decisions, review policy, conventions, instructions, task procedures, and templates. | — |

```
Browser
  │
  ▼
frontend/  (React + TypeScript, Vite dev server)
  │  HTTP JSON, /api/v1/
  ▼
backend/   (Django + Django REST Framework)
  │  Django ORM and migrations
  ▼
PostgreSQL
```

### Responsibilities of each layer

- **Frontend.** Owns presentation, navigation, forms, and client state. It calls
  the backend through `src/api/` and must not contain business rules that the
  backend also enforces. Build-time configuration is limited to public values.
- **Backend.** Owns the domain model, validation, authorization, business rules,
  and data access. Views translate HTTP to application calls; serializers
  validate and shape data; services hold multi-step workflows; models and
  migrations define persistence.
- **PostgreSQL.** Owns durable state, relational integrity, and transactional
  guarantees. Only the backend connects to it.
- **Documentation and AI guidance.** Owns the rules for humans and agents. It
  describes the system but must not duplicate code or configuration.

### Dependency rules

- Dependencies point from the UI toward storage: `frontend → backend → database`.
  Nothing points back.
- The frontend and backend share no runtime code or filesystem state. Their
  contract is the versioned REST API, whose OpenAPI schema is generated from the
  backend and committed at `docs/api/openapi.yaml`. The frontend generates
  `src/types/api/` from that snapshot and reaches the API only through
  `src/api/`.
- Within the frontend, `pages → features → components/lib → types`; shared code
  never imports pages or features.
- Within the backend, `urls → views → serializers/services → models`; apps do not
  query another app's tables directly.
- Prefer plain functions and Django/React primitives. Add an abstraction only
  when it removes real duplication or isolates a real boundary.

The rationale for these choices is recorded in
[`docs/decisions.md`](../decisions.md).

### Development workflow

GitHub Issues define the unit of work. Each issue is implemented on a dedicated
branch or Orca worktree, validated with the checks for the affected layer, and
delivered as a Pull Request for human review. Agents may open or update the Pull
Request but never merge or approve it. The commands, authentication
requirements, and troubleshooting are documented in
[`orca.md`](orca.md); the general rules are in [`AGENTS.md`](../../AGENTS.md).
Review standards, severity, evidence, and the approval contract are defined in
[`REVIEW.md`](../../REVIEW.md).

The GitHub Issue and Pull Request templates live in `.github/`. They keep the
scope, validation, and risks visible without duplicating the repository rules.

## Building blocks

The foundation separates three kinds of artifacts by **scope** and
**responsibility**:

| Artifact     | Location                                     | Scope                       | Responsibility                                                                       |
| ------------ | -------------------------------------------- | --------------------------- | ------------------------------------------------------------------------------------ |
| Instructions | `AGENTS.md`                                  | Every task, repository-wide | How agents behave here: principles, conventions, safety rules, delivery checklist.   |
| Skills       | `.agents/skills/<name>/SKILL.md`             | A specific kind of task     | Focused, reusable procedures an agent loads only when relevant.                      |
| Tools        | External, catalogued in `docs/ai/tooling.md` | Per capability              | Executable capabilities (CLIs, MCP servers, services) that agents and humans invoke. |

Supporting documentation lives in `docs/ai/`:

- `architecture.md` — this file: how the components fit together.
- `conventions.md` — shared coding and repository conventions.
- `orca.md` — issue-to-pull-request workflow, Orca commands, and GitHub
  authentication.
- `skills.md` — installed Agent Skills, provenance, and maintenance.
- `tooling.md` — catalog of tools by status (in use, proposed, pending
  evaluation).

The canonical review policy is the root [`REVIEW.md`](../../REVIEW.md); it is
referenced rather than duplicated here.

Fundamental architecture decisions are recorded in
[`docs/decisions.md`](../decisions.md). Application layout is documented in
`frontend/README.md` and `backend/README.md`.

## Responsibilities of `AGENTS.md`

`AGENTS.md` is the **single, provider-independent source of truth** for general
agent behavior in this repository. Review criteria, severity, evidence, and
human approval are owned by the root [`REVIEW.md`](../../REVIEW.md) and are not
restated here. `AGENTS.md` must remain:

- **General**: it applies to every task, not to one specific workflow.
- **Stable**: it changes only when the repository's ground rules change.
- **Short**: detailed, task-specific guidance belongs in a skill or in
  `docs/ai/`.

If guidance is only relevant to one kind of task, it belongs in a skill, not in
`AGENTS.md`.

## How the components relate

```
AGENTS.md  ── general rules, always in effect ─────────────┐
                                                           │ guide how to use
.agents/skills/<name>/SKILL.md ── task-specific procedure ─┤
                                                           │
docs/ai/tooling.md ── available capabilities ──────────────┘
```

- `AGENTS.md` tells an agent _how to work_ in general.
- A skill tells an agent _how to perform a specific kind of task_.
- A tool provides the _capability_ the agent or human invokes.
- `docs/ai/conventions.md` holds conventions shared by instructions, skills,
  and code.

A skill may reference tools, but it must not restate general rules from
`AGENTS.md`. It should link to them instead.

## Avoiding duplicated configuration

1. **One source of truth per concern.** Every rule lives in exactly one place.
2. **Reference, do not copy.** Link to `AGENTS.md`, `docs/ai/`, or another
   skill rather than repeating their text.
3. **Prefer general over specific.** Put a rule in `AGENTS.md` unless it applies
   to only one task type, in which case it belongs in a skill.
4. **Fail loudly on conflict.** If two documents contradict each other, treat it
   as a bug and fix the weaker one.

## Provider independence

The foundation must not depend on a specific agent, model, or vendor. To keep
it portable:

- Store instructions and skills as plain Markdown under version control.
- Avoid vendor-specific syntax in `AGENTS.md` and skills.
- When a tool requires a different format, add a **thin adapter** in that
  tool's configuration that points back to the canonical file. Do not duplicate
  content.
- Keep tool choices documented in `docs/ai/tooling.md` rather than hard-coded
  into instructions.

## Adding a new tool

1. Identify the capability the tool provides and its category in
   `docs/ai/tooling.md`.
2. Add it with an explicit status: **in use**, **proposed**, or **pending
   evaluation**.
3. Justify it: what problem it solves and why existing tools are insufficient.
4. If adopted, integrate through a thin adapter that references the canonical
   instructions. Do not fork the rules.
5. Update `AGENTS.md` only if adoption changes the general workflow.

## Pending decisions

The following are intentionally unresolved and should be decided in future
iterations:

- **PENDING**: whether to adopt a Python type checker (for example Mypy) and
  coverage measurement (see `tooling.md`).
- **PENDING**: which MCP servers, if any, to use and for which capabilities.
- **PENDING**: whether skill updates should be automated with review gates; for
  now they are manual (see [`skills.md`](skills.md)).
- **PENDING**: the project identity (the root `pyproject.toml` name still
  reflects an earlier temporary project and may need to be renamed or removed).

Orca was adopted as the workspace and agent orchestration layer instead of a
custom orchestrator; its operational workflow is documented in
[`orca.md`](orca.md).
