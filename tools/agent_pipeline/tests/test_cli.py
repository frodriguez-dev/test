"""End-to-end CLI behavior with fake executables."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from agent_pipeline.quality.cli import main

from tests.support import write_quality_config

REQUIRED_KEYS = {
    "id",
    "layer",
    "command",
    "working_directory",
    "status",
    "exit_code",
    "duration_seconds",
    "summary",
    "output_path",
    "required",
}


def _run(repo: Path, *args: str) -> int:
    return main(["quality", "--repo-root", str(repo), *args])


def _report(repo: Path) -> dict:
    return json.loads((repo / ".quality/quality.json").read_text(encoding="utf-8"))


def _statuses(repo: Path) -> dict[str, str]:
    return {check["id"]: check["status"] for check in _report(repo)["checks"]}


def test_gate_passes_and_writes_contract(repo: Path, fake_tools: Path) -> None:
    assert _run(repo) == 0

    report = _report(repo)
    assert report["schema_version"] == 1
    assert report["status"] == "PASS"
    assert report["exit_code"] == 0
    assert report["summary"]["total"] == 14
    assert report["summary"]["required"] == 12
    assert "python" in report["tool_versions"]

    for check in report["checks"]:
        assert REQUIRED_KEYS <= set(check)
        assert check["working_directory"].startswith(str(repo.resolve()))
        assert isinstance(check["command"], list)
        assert check["command"]

    statuses = _statuses(repo)
    assert statuses["backend-lint"] == "PASS"
    assert statuses["frontend-build"] == "PASS"
    assert statuses["uv-audit"] == "SKIP"
    assert statuses["pnpm-audit"] == "SKIP"


def test_human_output_lists_every_check(repo: Path, fake_tools: Path, capsys) -> None:
    assert _run(repo) == 0

    output = capsys.readouterr().out
    assert "Quality gate: PASS (exit 0)" in output
    assert "backend-lint" in output
    assert "uv-audit" in output
    assert "JSON report:" in output


def test_backend_failure_exits_one_and_still_runs_frontend(
    repo: Path, fake_tools: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_FAIL_BACKEND_TEST", "1")

    assert _run(repo) == 1

    statuses = _statuses(repo)
    assert statuses["backend-test"] == "FAIL"
    assert statuses["backend-lint"] == "PASS"
    assert statuses["frontend-test"] == "PASS"
    report = _report(repo)
    assert report["status"] == "FAIL"
    assert report["exit_code"] == 1


def test_frontend_failure_propagates(
    repo: Path, fake_tools: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_FAIL_FRONTEND_TEST", "1")

    assert _run(repo) == 1
    assert _statuses(repo)["frontend-test"] == "FAIL"


def test_backend_and_frontend_failures_are_both_reported(
    repo: Path, fake_tools: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_FAIL_BACKEND_TEST", "1")
    monkeypatch.setenv("FAKE_FAIL_FRONTEND_BUILD", "1")

    assert _run(repo) == 1
    statuses = _statuses(repo)
    assert statuses["backend-test"] == "FAIL"
    assert statuses["frontend-build"] == "FAIL"


def test_complexity_failure_exits_one(
    repo: Path, fake_tools: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_FAIL_COMPLEXITY", "1")

    assert _run(repo) == 1
    statuses = _statuses(repo)
    assert statuses["backend-complexity"] == "FAIL"
    assert statuses["frontend-complexity"] == "PASS"


def test_missing_tool_exits_two(repo: Path, tmp_path: Path, monkeypatch) -> None:
    empty_bin = tmp_path / "empty-bin"
    empty_bin.mkdir()
    monkeypatch.setenv("PATH", str(empty_bin))

    assert _run(repo) == 2

    report = _report(repo)
    assert report["status"] == "ERROR"
    assert report["exit_code"] == 2
    for check in report["checks"]:
        if check["required"]:
            assert check["status"] == "ERROR"
        else:
            assert check["status"] in {"ERROR", "SKIP"}
        assert check["status"] != "PASS"


def test_timeout_exits_two(repo: Path, fake_tools: Path, monkeypatch) -> None:
    monkeypatch.setenv("FAKE_SLEEP_LINT", "1")

    assert _run(repo, "--timeout", "backend-lint=0.2") == 2

    report = _report(repo)
    lint = next(check for check in report["checks"] if check["id"] == "backend-lint")
    assert lint["status"] == "ERROR"
    assert "Timed out" in lint["summary"]
    assert report["status"] == "ERROR"
    assert report["exit_code"] == 2


def test_required_security_skip_exits_two(repo: Path, fake_tools: Path) -> None:
    write_quality_config(
        repo / "tools/agent_pipeline/pyproject.toml",
        ruff_s="off",
    )

    assert _run(repo) == 2

    security = next(
        check for check in _report(repo)["checks"] if check["id"] == "python-security"
    )
    assert security["status"] == "ERROR"
    assert "Required check skipped" in security["summary"]


def test_required_network_check_skips_as_error(repo: Path, fake_tools: Path) -> None:
    write_quality_config(
        repo / "tools/agent_pipeline/pyproject.toml",
        uv_audit="required",
    )

    assert _run(repo) == 2

    audit = next(
        check for check in _report(repo)["checks"] if check["id"] == "uv-audit"
    )
    assert audit["required"] is True
    assert audit["status"] == "ERROR"
    assert "opt-in" in audit["summary"]


def test_invalid_configuration_exits_two_without_running(
    repo: Path, fake_tools: Path, capsys
) -> None:
    write_quality_config(
        repo / "tools/agent_pipeline/pyproject.toml",
        extra_root="surprise = 1",
    )

    assert _run(repo) == 2

    captured = capsys.readouterr()
    assert "configuration error" in captured.err
    assert "surprise" in captured.err
    assert not (repo / ".quality").exists()


def test_json_error_document_for_invalid_configuration(
    repo: Path, fake_tools: Path, capsys
) -> None:
    write_quality_config(
        repo / "tools/agent_pipeline/pyproject.toml",
        extra_root="surprise = 1",
    )

    assert _run(repo, "--json") == 2

    document = json.loads(capsys.readouterr().out)
    assert document["status"] == "ERROR"
    assert document["exit_code"] == 2
    assert "surprise" in document["error"]


def test_json_flag_prints_valid_json(repo: Path, fake_tools: Path, capsys) -> None:
    assert _run(repo, "--json", "--output", str(repo / "custom.json")) == 0

    document = json.loads(capsys.readouterr().out)
    assert document["schema_version"] == 1
    assert document["status"] == "PASS"
    assert (repo / "custom.json").is_file()


def test_network_checks_run_when_requested(repo: Path, fake_tools: Path) -> None:
    assert _run(repo, "--security-network") == 0

    statuses = _statuses(repo)
    assert statuses["uv-audit"] == "PASS"
    assert statuses["pnpm-audit"] == "PASS"


def test_fail_fast_stops_after_required_failure(
    repo: Path, fake_tools: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_FAIL_BACKEND_TEST", "1")

    assert _run(repo, "--fail-fast") == 1

    report = _report(repo)
    statuses = {check["id"]: check["status"] for check in report["checks"]}
    assert statuses["backend-test"] == "FAIL"
    assert statuses["frontend-typecheck"] == "SKIP"
    assert statuses["pnpm-audit"] == "SKIP"
    assert len(report["checks"]) == 14


def test_scoped_check_and_layer(repo: Path, fake_tools: Path) -> None:
    assert _run(repo, "--check", "backend-lint") == 0
    assert len(_report(repo)["checks"]) == 1

    assert _run(repo, "--layer", "frontend") == 0
    report = _report(repo)
    assert len(report["checks"]) == 5
    assert {check["layer"] for check in report["checks"]} == {"frontend"}


def test_list_checks(repo: Path, capsys) -> None:
    assert _run(repo, "--list-checks") == 0

    output = capsys.readouterr().out
    assert "backend-lint" in output
    assert "pnpm-audit" in output
    assert not (repo / ".quality").exists()
