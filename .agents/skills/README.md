# Agent skills

This directory holds **reusable skills**: focused, self-contained instructions
that an AI agent can load when a task matches the skill.

Skills complement [`AGENTS.md`](../../AGENTS.md). `AGENTS.md` applies to every
task; a skill applies only when its trigger conditions are met.

## Layout

```
.agents/skills/
├── README.md          # This file
├── _template/         # Copy this to start a new skill
│   └── SKILL.md
└── <skill-name>/
    └── SKILL.md
```

The `_template/` directory is a starting point, not a skill; it is never meant
to be applied directly.

Installed third-party skills are listed, with provenance and maintenance
instructions, in [`docs/ai/skills.md`](../../docs/ai/skills.md). Claude Code
reads them through relative links in `.claude/skills/`; do not create copies
there.

## Anatomy of a skill

Each skill is a directory containing a `SKILL.md` file with:

- **Front matter** (`name`, `description`): metadata used to discover and
  select the skill. The `description` should state *what the skill does* and
  *when to use it*.
- **Purpose**: the problem the skill solves.
- **Instructions**: the concrete steps or rules the agent must follow.
- **When to use it**: the conditions under which the skill applies.
- **When not to use it**: boundaries and counter-indications.

Keep skills small and specific. If a skill grows to cover unrelated concerns,
split it.

## Discovering skills

1. List the directories under `.agents/skills/` (ignoring `_template/` and
   `README.md`), or read the catalog in [`docs/ai/skills.md`](../../docs/ai/skills.md).
2. Read the `description` in each `SKILL.md` front matter.
3. Load the skill whose description matches the current task.
4. Do not install a new skill without explicit authorization.

Because this directory is plain Markdown, the same skills can be consumed by
different agent tools. If a tool needs a different format, add a thin adapter
there instead of duplicating the skill content — see
[`docs/ai/architecture.md`](../../docs/ai/architecture.md).

## Creating a skill

1. Copy `_template/SKILL.md` into a new directory named after the skill
   (lowercase, hyphen-separated).
2. Fill in the front matter, purpose, instructions, and application criteria.
3. Keep the instructions concrete and verifiable.
4. Update the description so the skill is discoverable.

Do not create a skill until its purpose is clear. Placeholder or empty skills
should not be committed.
