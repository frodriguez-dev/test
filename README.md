# AI-Assisted Development Sandbox

This repository is a sandbox for experimenting with **software development
assisted by AI agents**. It pairs small, self-contained example
implementations with a provider-independent foundation for agent instructions,
skills, and documentation.

## Purpose

- Provide a safe place to try out AI-agent development workflows.
- Keep a clear foundation that both humans and agents can follow.
- Preserve small, working implementations as references.

## Repository layout

```
.
├── AGENTS.md            # Instructions for AI coding agents
├── README.md            # This file
├── calculator.py        # Example module used by the root test suite
├── tests/               # pytest suite for calculator.py
├── experiments/         # Self-contained example applications
│   ├── csv_analyzer/    # CSV sales analyzer (standard library only)
│   └── task_manager/    # Console task manager with JSON persistence
├── .agents/
│   └── skills/          # Reusable agent skills and their template
└── docs/
    └── ai/              # Architecture, conventions, and tooling notes
```

## Requirements

- Python 3.10 or higher (see `pyproject.toml`).
- `pytest` for the root test suite (development dependency).

## Getting started

Run the root test suite:

```bash
python -m pytest
```

Run the example applications:

```bash
python -m experiments.csv_analyzer experiments/csv_analyzer/ventas.csv
python -m experiments.task_manager list
```

Run the example applications' test suites:

```bash
python -m unittest discover -s experiments/csv_analyzer/tests -t .
python -m unittest discover -s experiments/task_manager/tests -v
```

See each experiment's own `README.md` for details.

## AI development foundation

- [`AGENTS.md`](AGENTS.md) — how agents should work in this repository.
- [`docs/ai/architecture.md`](docs/ai/architecture.md) — how instructions,
  skills, and tools fit together.
- [`docs/ai/conventions.md`](docs/ai/conventions.md) — coding and repository
  conventions.
- [`docs/ai/tooling.md`](docs/ai/tooling.md) — tools that are used, proposed,
  or still being evaluated.
- [`.agents/skills/`](.agents/skills/README.md) — reusable agent skills.

## Status

This is an early foundation. Orchestration, complex skills, and most tooling
integrations are intentionally out of scope for now. Open questions are tracked
as *PENDING* in the `docs/ai/` documents rather than assumed.
