"""JSON contract and human rendering."""

from __future__ import annotations

import json
from pathlib import Path

from agent_pipeline.quality.models import (
    CheckResult,
    GateReport,
    Layer,
    Status,
    evaluate_gate,
)
from agent_pipeline.quality.report import render_human, report_to_json, write_report


def _result(
    check_id: str,
    status: Status,
    *,
    required: bool = True,
    exit_code: int | None = 0,
) -> CheckResult:
    return CheckResult(
        id=check_id,
        layer=Layer.BACKEND,
        command=("fake", "--check"),
        working_directory=Path("/repo/backend"),
        required=required,
        status=status,
        exit_code=exit_code,
        duration_seconds=0.5,
        summary=f"{check_id} summary",
    )


def _report(
    checks: tuple[CheckResult, ...], status: Status, exit_code: int
) -> GateReport:
    return GateReport(
        status=status,
        exit_code=exit_code,
        started_at="2026-01-01T00:00:00+00:00",
        finished_at="2026-01-01T00:00:01+00:00",
        duration_seconds=1.0,
        checks=checks,
    )


def test_json_shape_contains_the_documented_fields(tmp_path: Path) -> None:
    report = _report(
        (
            _result("backend-lint", Status.PASS),
            _result("uv-audit", Status.SKIP, required=False, exit_code=None),
        ),
        Status.PASS,
        0,
    )

    document = json.loads(report_to_json(report))

    assert document["schema_version"] == 1
    assert document["status"] == "PASS"
    assert document["exit_code"] == 0
    assert document["summary"] == {
        "total": 2,
        "passed": 1,
        "failed": 0,
        "skipped": 1,
        "errors": 0,
        "required": 1,
    }
    assert document["tool_versions"] == {}
    first = document["checks"][0]
    assert first == {
        "id": "backend-lint",
        "layer": "backend",
        "command": ["fake", "--check"],
        "working_directory": "/repo/backend",
        "status": "PASS",
        "exit_code": 0,
        "duration_seconds": 0.5,
        "summary": "backend-lint summary",
        "output_path": None,
        "required": True,
    }

    path = write_report(report, tmp_path / "nested" / "quality.json")
    assert json.loads(path.read_text(encoding="utf-8"))["status"] == "PASS"


def test_human_summary_renders_problems_and_report_path(tmp_path: Path) -> None:
    log = tmp_path / ".quality/logs/backend-test.log"
    log.parent.mkdir(parents=True)
    log.write_text("failure line one\nfailure line two\n", encoding="utf-8")
    failed = CheckResult(
        id="backend-test",
        layer=Layer.BACKEND,
        command=("make", "backend-test"),
        working_directory=tmp_path,
        required=True,
        status=Status.FAIL,
        exit_code=1,
        duration_seconds=2.0,
        summary="Command exited with code 1.",
        output_path=".quality/logs/backend-test.log",
    )
    report = _report((failed,), Status.FAIL, 1)

    text = render_human(
        report,
        repo_root=tmp_path,
        report_path=tmp_path / ".quality/quality.json",
    )

    assert "Quality gate: FAIL (exit 1)" in text
    assert "make backend-test" in text
    assert "failure line two" in text
    assert "Full output: .quality/logs/backend-test.log" in text
    assert "JSON report:" in text


def test_evaluate_gate_precedence() -> None:
    passing = _result("pass", Status.PASS)
    failing = _result("fail", Status.FAIL, exit_code=1)
    error = _result("error", Status.ERROR, exit_code=None)
    skipped_optional = _result("optional", Status.SKIP, required=False, exit_code=None)

    assert evaluate_gate((passing, skipped_optional)) == (Status.PASS, 0)
    assert evaluate_gate((passing, failing)) == (Status.FAIL, 1)
    assert evaluate_gate((failing, error)) == (Status.ERROR, 2)
    assert evaluate_gate((error,)) == (Status.ERROR, 2)
