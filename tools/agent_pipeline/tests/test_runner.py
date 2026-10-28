"""Runner behavior: statuses, timeouts, truncation, and gate semantics."""

from __future__ import annotations

from pathlib import Path

from agent_pipeline.quality.models import Status
from agent_pipeline.quality.runner import run_check, run_quality, truncate_output

from tests.support import DEFINITELY_MISSING, make_spec


def _run(spec, tmp_path: Path):
    return run_check(
        spec,
        log_dir=tmp_path / "logs",
        repo_root=tmp_path,
        max_output_bytes=4096,
    )


def test_passing_check(tmp_path: Path, fake_tools: Path) -> None:
    result = _run(make_spec(tmp_path, ("noisy",), timeout_seconds=5), tmp_path)

    assert result.status is Status.PASS
    assert result.exit_code == 0
    assert result.required is True
    assert result.duration_seconds >= 0
    assert result.output_path is not None
    assert (tmp_path / result.output_path).is_file()


def test_failing_check_reports_exit_code(tmp_path: Path) -> None:
    script = tmp_path / "fail"
    script.write_text("#!/bin/sh\necho boom\nexit 7\n", encoding="utf-8")
    script.chmod(0o755)

    result = _run(make_spec(tmp_path, (str(script),)), tmp_path)

    assert result.status is Status.FAIL
    assert result.exit_code == 7
    assert "exited with code 7" in result.summary


def test_timeout_is_an_error(tmp_path: Path) -> None:
    result = _run(
        make_spec(tmp_path, ("sleep", "10"), timeout_seconds=0.2),
        tmp_path,
    )

    assert result.status is Status.ERROR
    assert "Timed out after 0.2s" in result.summary
    assert result.duration_seconds < 5


def test_missing_tool_is_an_error(tmp_path: Path) -> None:
    result = _run(
        make_spec(tmp_path, (DEFINITELY_MISSING,)),
        tmp_path,
    )

    assert result.status is Status.ERROR
    assert result.exit_code is None
    assert "Executable not found" in result.summary


def test_optional_skip_is_skip(tmp_path: Path) -> None:
    result = _run(
        make_spec(
            tmp_path,
            (DEFINITELY_MISSING,),
            required=False,
            skip_reason="disabled in configuration",
        ),
        tmp_path,
    )

    assert result.status is Status.SKIP
    assert "disabled in configuration" in result.summary
    assert result.exit_code is None


def test_required_skip_is_an_error(tmp_path: Path) -> None:
    result = _run(
        make_spec(
            tmp_path,
            (DEFINITELY_MISSING,),
            required=True,
            skip_reason="missing required configuration",
        ),
        tmp_path,
    )

    assert result.status is Status.ERROR
    assert "Required check skipped" in result.summary


def test_output_is_truncated_with_marker(tmp_path: Path, fake_tools: Path) -> None:
    result = _run(
        make_spec(tmp_path, ("noisy",)),
        tmp_path,
    )

    assert result.output_path is not None
    artifact = (tmp_path / result.output_path).read_text(encoding="utf-8")
    assert "output truncated" in artifact
    assert len(artifact) < 6000


def test_truncate_output_keeps_head_and_tail() -> None:
    text = truncate_output(b"a" * 100 + b"z" * 100, 40)

    assert "output truncated" in text
    assert text.startswith("a")
    assert text.endswith("z")


def test_gate_pass_requires_only_required_checks(tmp_path: Path) -> None:
    optional_failure = tmp_path / "optional-fail"
    optional_failure.write_text("#!/bin/sh\nexit 4\n", encoding="utf-8")
    optional_failure.chmod(0o755)

    report = run_quality(
        (
            make_spec(tmp_path, ("true",)),
            make_spec(
                tmp_path,
                (str(optional_failure),),
                check_id="optional-check",
                required=False,
            ),
        ),
        repo_root=tmp_path,
        log_dir=tmp_path / "logs",
        max_output_bytes=4096,
    )

    assert report.status is Status.PASS
    assert report.exit_code == 0
    assert report.checks[1].status is Status.FAIL
    assert report.counts()["failed"] == 1


def test_gate_error_takes_precedence_over_failure(tmp_path: Path) -> None:
    report = run_quality(
        (
            make_spec(tmp_path, ("false",), check_id="fails"),
            make_spec(
                tmp_path,
                (DEFINITELY_MISSING,),
                check_id="errors",
            ),
        ),
        repo_root=tmp_path,
        log_dir=tmp_path / "logs",
        max_output_bytes=4096,
    )

    assert report.status is Status.ERROR
    assert report.exit_code == 2


def test_fail_fast_marks_remaining_checks_skipped(tmp_path: Path) -> None:
    report = run_quality(
        (
            make_spec(tmp_path, ("false",), check_id="first"),
            make_spec(tmp_path, ("true",), check_id="second"),
        ),
        repo_root=tmp_path,
        log_dir=tmp_path / "logs",
        max_output_bytes=4096,
        fail_fast=True,
    )

    assert report.exit_code == 1
    assert report.checks[0].status is Status.FAIL
    assert report.checks[1].status is Status.SKIP
    assert "fail-fast" in report.checks[1].summary
