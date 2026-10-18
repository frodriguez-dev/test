"""Allow running the CLI with ``python -m experiments.task_manager``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
