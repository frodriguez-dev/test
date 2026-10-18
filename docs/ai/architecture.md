# AI development architecture

This document describes how the pieces of the AI-assisted development
foundation relate to each other, and the principles that keep them consistent.

It is a starting point for future decisions, not a final specification.

## Building blocks

The foundation separates three kinds of artifacts by **scope** and
**responsibility**:

| Artifact | Location | Scope | Responsibility |
| --- | --- | --- | --- |
| Instructions | `AGENTS.md` | Every task, repository-wide | How agents behave here: principles, conventions, safety rules, delivery checklist. |
| Skills | `.agents/skills/<name>/SKILL.md` | A specific kind of task | Focused, reusable procedures an agent loads only when relevant. |
| Tools | External, catalogued in `docs/ai/tooling.md` | Per capability | Executable capabilities (CLIs, MCP servers, services) that agents and humans invoke. |

Supporting documentation lives in `docs/ai/`:

- `architecture.md` — this file: how the components fit together.
- `conventions.md` — shared coding and repository conventions.
- `tooling.md` — catalog of tools by status (in use, proposed, pending
  evaluation).

## Responsibilities of `AGENTS.md`

`AGENTS.md` is the **single, provider-independent source of truth** for agent
behavior in this repository. It must remain:

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

- `AGENTS.md` tells an agent *how to work* in general.
- A skill tells an agent *how to perform a specific kind of task*.
- A tool provides the *capability* the agent or human invokes.
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

- **PENDING**: whether an orchestration layer is needed and, if so, which one.
- **PENDING**: which linters, formatters, and type checkers to adopt (see
  `tooling.md`).
- **PENDING**: which MCP servers, if any, to use and for which capabilities.
- **PENDING**: how skills should be versioned and shared across repositories.
- **PENDING**: whether the example implementations in `experiments/` should
  eventually move to their own repositories.
