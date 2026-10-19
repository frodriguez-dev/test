# AI-Assisted Development Foundation

This repository is a clean, provider-independent foundation for **software
development assisted by AI agents**. It provides shared instructions, a skills
system, and architecture documentation that humans and agents can both follow
and build on. It is also the monorepo for the React and Django applications
described below.

## Planned stack

The backend is initialized with Django, Django REST Framework, PostgreSQL, and
uv; the frontend is initialized with React, TypeScript, Vite, and pnpm. Issue #16
established the structure, issue #18 added the frontend toolchain, issue #19
initialized the backend, and issue #17 added Django REST Framework and the first
endpoint (`GET /api/health/`).

| Layer | Stack | Location |
| --- | --- | --- |
| Frontend | React, TypeScript, Vite, pnpm | `frontend/` |
| Backend | Django, Django REST Framework, uv | `backend/` |
| Database | PostgreSQL | Accessed by the backend only |
| API | REST/JSON under `/api/v1/` (plus `GET /api/health/`) | `backend/` |

## Purpose

- Establish a clear, minimal base for AI-assisted development.
- Keep instructions, skills, and tooling consistent and free of duplication.
- Stay independent of any specific agent, model, or vendor.
- Keep frontend, backend, and documentation in one repository with explicit
  boundaries.

## Repository layout

```
.
├── AGENTS.md            # Instructions for AI coding agents
├── README.md            # This file
├── THIRD_PARTY_NOTICES.md  # Licenses for vendored skills
├── skills-lock.json     # Agent Skills installer lock file
├── pyproject.toml       # Provisional root Python metadata (moves to backend/)
├── .agents/
│   └── skills/          # Installed skills, template, and catalog
├── .claude/
│   └── skills/          # Relative links to the canonical skills
├── backend/             # Django REST API (Django + DRF + PostgreSQL initialized)
│   └── README.md        # Backend structure, setup, and boundaries
├── frontend/            # React SPA (initialized: React, TypeScript, Vite, pnpm)
│   └── README.md        # Frontend structure, commands, and boundaries
└── docs/
    ├── decisions.md     # Fundamental architecture decisions
    └── ai/              # Architecture, conventions, tooling, and skills notes
```

## Getting started

Read the foundation in this order:

1. [`AGENTS.md`](AGENTS.md) — how agents should work in this repository.
2. [`docs/ai/architecture.md`](docs/ai/architecture.md) — how the application
   layers and the AI foundation fit together.
3. [`docs/decisions.md`](docs/decisions.md) — why the stack and boundaries were
   chosen.
4. [`docs/ai/conventions.md`](docs/ai/conventions.md) — coding, repository, and
   dependency conventions.
5. [`docs/ai/tooling.md`](docs/ai/tooling.md) — tools that are used, proposed,
   or still being evaluated.
6. [`docs/ai/skills.md`](docs/ai/skills.md) — installed Agent Skills,
   provenance, and maintenance.
7. [`.agents/skills/`](.agents/skills/README.md) — reusable agent skills.

## Status

This is an early foundation. The monorepo structure is defined and the backend
(Django, Django REST Framework, and PostgreSQL) and frontend (React, TypeScript,
Vite, and pnpm) toolchains are initialized. The backend exposes the
infrastructure endpoint `GET /api/health/` and has tests for it; there are no
business models or business endpoints yet. Unresolved choices are tracked as
*PENDING* in the `docs/ai/` documents rather than assumed. A first set of
professional Agent Skills is installed and versioned in the repository; see
[`docs/ai/skills.md`](docs/ai/skills.md).
