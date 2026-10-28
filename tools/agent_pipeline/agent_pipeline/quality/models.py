"""Data model shared by the quality-gate runner, CLI, and report writers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_INCOMPLETE = 2


class Status(StrEnum):
    """Result of a single check or of the gate as a whole."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


class Layer(StrEnum):
    """Logical group a check belongs to."""

    BACKEND = "backend"
    FRONTEND = "frontend"
    COMPLEXITY = "complexity"
    SECURITY = "security"


@dataclass(frozen=True)
class CheckSpec:
    """Declarative description of one command the gate must run.

    ``command`` is executed as an argument vector with ``shell=False``.
    ``working_directory`` must be absolute so results do not depend on where
    the CLI was started.
    """

    id: str
    layer: Layer
    description: str
    command: tuple[str, ...]
    working_directory: Path
    required: bool = True
    timeout_seconds: float = 600.0
    env: Mapping[str, str] = field(default_factory=dict)
    skip_reason: str | None = None
    network: bool = False


@dataclass(frozen=True)
class CheckResult:
    """Outcome of running :class:`CheckSpec`."""

    id: str
    layer: Layer
    command: tuple[str, ...]
    working_directory: Path
    required: bool
    status: Status
    exit_code: int | None
    duration_seconds: float
    summary: str
    output_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return the stable JSON representation of this check."""
        return {
            "id": self.id,
            "layer": self.layer.value,
            "command": list(self.command),
            "working_directory": str(self.working_directory),
            "status": self.status.value,
            "exit_code": self.exit_code,
            "duration_seconds": self.duration_seconds,
            "summary": self.summary,
            "output_path": self.output_path,
            "required": self.required,
        }


@dataclass(frozen=True)
class GateReport:
    """Aggregated result for one gate invocation."""

    status: Status
    exit_code: int
    started_at: str
    finished_at: str
    duration_seconds: float
    checks: tuple[CheckResult, ...]
    tool_versions: Mapping[str, str] = field(default_factory=dict)

    def counts(self) -> dict[str, int]:
        """Count results by status plus the number of required checks."""
        counts = {
            "total": len(self.checks),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "required": sum(1 for check in self.checks if check.required),
        }
        for check in self.checks:
            if check.status is Status.PASS:
                counts["passed"] += 1
            elif check.status is Status.FAIL:
                counts["failed"] += 1
            elif check.status is Status.SKIP:
                counts["skipped"] += 1
            else:
                counts["errors"] += 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        """Return the stable JSON representation of this report."""
        return {
            "schema_version": SCHEMA_VERSION,
            "status": self.status.value,
            "exit_code": self.exit_code,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
            "summary": self.counts(),
            "tool_versions": dict(sorted(self.tool_versions.items())),
            "checks": [check.to_dict() for check in self.checks],
        }


def evaluate_gate(checks: tuple[CheckResult, ...]) -> tuple[Status, int]:
    """Apply the documented gate semantics.

    A required error or timeout means the result is incomplete and takes
    precedence over a plain failure because the gate cannot vouch for the
    unexecuted work. ``SKIP`` for a required check is converted to ``ERROR``
    by the runner before evaluation.
    """
    required = tuple(check for check in checks if check.required)
    if any(check.status is Status.ERROR for check in required):
        return Status.ERROR, EXIT_INCOMPLETE
    if any(check.status is Status.FAIL for check in required):
        return Status.FAIL, EXIT_FAIL
    return Status.PASS, EXIT_PASS
