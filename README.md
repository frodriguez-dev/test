# AI-Assisted Development Foundation

This repository is a clean, provider-independent foundation for **software
development assisted by AI agents**. It provides shared instructions, a skills
system, and architecture documentation that humans and agents can both follow
and build on.

## Purpose

- Establish a clear, minimal base for AI-assisted development.
- Keep instructions, skills, and tooling consistent and free of duplication.
- Stay independent of any specific agent, model, or vendor.

## Repository layout

```
.
├── AGENTS.md            # Instructions for AI coding agents
├── README.md            # This file
├── .agents/
│   └── skills/          # Reusable agent skills and their template
└── docs/
    └── ai/              # Architecture, conventions, and tooling notes
```

## Getting started

Read the foundation in this order:

1. [`AGENTS.md`](AGENTS.md) — how agents should work in this repository.
2. [`docs/ai/architecture.md`](docs/ai/architecture.md) — how instructions,
   skills, and tools fit together.
3. [`docs/ai/conventions.md`](docs/ai/conventions.md) — coding and repository
   conventions.
4. [`docs/ai/tooling.md`](docs/ai/tooling.md) — tools that are used, proposed,
   or still being evaluated.
5. [`.agents/skills/`](.agents/skills/README.md) — reusable agent skills.

## Status

This is an early foundation. It intentionally contains no application code,
tests, or orchestration yet. Unresolved choices are tracked as *PENDING* in the
`docs/ai/` documents rather than assumed.
