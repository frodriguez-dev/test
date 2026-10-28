"""Render gate results as a human summary or a JSON document."""

from __future__ import annotations

import json
import shlex
from pathlib import Path

from .models import CheckResult, GateReport, Status

EXCERPT_LIMIT = 4000
EXCERPT_LINES = 20


def report_to_json(report: GateReport) -> str:
    """Serialize a report with a trailing newline."""
    return json.dumps(report.to_dict(), indent=2) + "\n"


def write_report(report: GateReport, path: Path) -> Path:
    """Write the JSON report, creating parent directories as needed."""
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_to_json(report), encoding="utf-8")
    return path


def _command_text(check: CheckResult) -> str:
    return " ".join(shlex.quote(part) for part in check.command)


def _table(report: GateReport) -> list[str]:
    headers = ("LAYER", "CHECK", "STATUS", "EXIT", "TIME", "COMMAND")
    rows = [
        (
            check.layer.value,
            check.id,
            check.status.value,
            "-" if check.exit_code is None else str(check.exit_code),
            f"{check.duration_seconds:.1f}s",
            _command_text(check),
        )
        for check in report.checks
    ]
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    # Keep the command column readable without hiding the other columns.
    widths[-1] = min(widths[-1], 64)
    lines = [
        "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers))
    ]
    for row in rows:
        cells = []
        for index, cell in enumerate(row):
            if index == len(row) - 1 and len(cell) > widths[index]:
                cell = cell[: widths[index] - 3] + "..."
            cells.append(cell.ljust(widths[index]))
        lines.append("  ".join(cells))
    return lines


def _artifact_tail(repo_root: Path, output_path: str) -> str:
    artifact = repo_root / output_path
    try:
        text = artifact.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    tail = text[-EXCERPT_LIMIT:]
    lines = tail.splitlines()
    if len(lines) > EXCERPT_LINES:
        lines = ["[... output truncated ...]"] + lines[-EXCERPT_LINES:]
    return "\n".join(lines)


def render_human(
    report: GateReport,
    *,
    repo_root: Path,
    report_path: Path | None = None,
) -> str:
    """Build the human-readable summary printed by the CLI."""
    counts = report.counts()
    lines = [
        f"Quality gate: {report.status.value} (exit {report.exit_code})",
        (
            f"Checks: {counts['total']} total, {counts['passed']} passed, "
            f"{counts['failed']} failed, {counts['skipped']} skipped, "
            f"{counts['errors']} errors ({counts['required']} required)"
        ),
        f"Duration: {report.duration_seconds:.1f}s",
        "",
        *_table(report),
    ]

    problems = [
        check for check in report.checks if check.status in {Status.FAIL, Status.ERROR}
    ]
    for check in problems:
        lines.extend(
            [
                "",
                (f"--- {check.id} ({check.status.value}, exit {check.exit_code}) ---"),
                f"Command: {_command_text(check)}",
                f"Working directory: {check.working_directory}",
                check.summary,
            ]
        )
        if check.output_path:
            excerpt = _artifact_tail(repo_root, check.output_path)
            if excerpt:
                lines.append(excerpt)
            lines.append(f"Full output: {check.output_path}")

    if report_path is not None:
        lines.extend(["", f"JSON report: {report_path}"])
    return "\n".join(lines) + "\n"
