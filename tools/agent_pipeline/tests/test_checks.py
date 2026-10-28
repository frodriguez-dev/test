"""Check catalog construction, thresholds, security modes, and selection."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
from agent_pipeline.quality.checks import build_checks, select_checks
from agent_pipeline.quality.config import ConfigError, load_config

from tests.support import make_repo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMITTED_CONFIG = PROJECT_ROOT / "pyproject.toml"

EXPECTED_IDS = {
    "backend-lint",
    "backend-format",
    "backend-typecheck",
    "backend-test",
    "frontend-typecheck",
    "frontend-lint",
    "frontend-format",
    "frontend-test",
    "frontend-build",
    "backend-complexity",
    "frontend-complexity",
    "python-security",
    "uv-audit",
    "pnpm-audit",
}


def _catalog(tmp_path: Path, **kwargs):
    repo = make_repo(tmp_path / "repo")
    config = load_config(COMMITTED_CONFIG)
    return repo, build_checks(config, repo, **kwargs)


def test_catalog_has_the_required_checks(tmp_path: Path) -> None:
    _, checks = _catalog(tmp_path)

    assert {check.id for check in checks} == EXPECTED_IDS
    assert all(check.working_directory.is_absolute() for check in checks)
    assert all(check.command for check in checks)
    assert all(check.timeout_seconds > 0 for check in checks)


def test_commands_delegate_to_existing_make_targets(tmp_path: Path) -> None:
    _, checks = _catalog(tmp_path)
    by_id = {check.id: check for check in checks}

    assert by_id["backend-test"].command == ("make", "backend-test")
    assert by_id["frontend-build"].command == ("make", "frontend-build")
    assert by_id["backend-lint"].command == (
        "uv",
        "run",
        "ruff",
        "check",
        "--color=never",
        ".",
    )
    assert by_id["frontend-test"].command == ("pnpm", "test")
    assert all("shell" not in check.command for check in checks)


def test_network_checks_are_skipped_by_default(tmp_path: Path) -> None:
    _, checks = _catalog(tmp_path)
    by_id = {check.id: check for check in checks}

    assert by_id["uv-audit"].required is False
    assert by_id["pnpm-audit"].required is False
    assert "opt-in" in (by_id["uv-audit"].skip_reason or "")
    assert "opt-in" in (by_id["pnpm-audit"].skip_reason or "")


def test_security_network_flag_enables_network_checks(tmp_path: Path) -> None:
    _, checks = _catalog(tmp_path, security_network=True)
    by_id = {check.id: check for check in checks}

    assert by_id["uv-audit"].skip_reason is None
    assert by_id["pnpm-audit"].skip_reason is None


def test_disabled_ruff_security_remains_required(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    config = load_config(COMMITTED_CONFIG)
    config = replace(
        config,
        security=replace(config.security, ruff_s="off"),
    )

    checks = build_checks(config, repo)
    security = next(check for check in checks if check.id == "python-security")

    assert security.required is True
    assert security.skip_reason is not None


def test_complexity_thresholds_are_injected(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    config = load_config(COMMITTED_CONFIG)
    config = replace(
        config,
        python_complexity=7,
        typescript_complexity=8,
    )

    checks = build_checks(config, repo)
    by_id = {check.id: check for check in checks}

    python_command = by_id["backend-complexity"].command
    assert "lint.mccabe.max-complexity=7" in python_command

    typescript_command = by_id["frontend-complexity"].command
    rule = json.loads(typescript_command[-1])
    assert rule == {"complexity": ["error", 8]}


def test_select_by_layer(tmp_path: Path) -> None:
    _, checks = _catalog(tmp_path)

    frontend = select_checks(checks, layers=["frontend"])
    security = select_checks(checks, layers=["security"])
    complexity = select_checks(checks, layers=["complexity"])

    assert {check.id for check in frontend} == {
        "frontend-typecheck",
        "frontend-lint",
        "frontend-format",
        "frontend-test",
        "frontend-build",
    }
    assert {check.id for check in security} == {
        "python-security",
        "uv-audit",
        "pnpm-audit",
    }
    assert {check.id for check in complexity} == {
        "backend-complexity",
        "frontend-complexity",
    }


def test_select_by_check_id_and_combined_filters(tmp_path: Path) -> None:
    _, checks = _catalog(tmp_path)

    selected = select_checks(checks, layers=["backend"], check_ids=["backend-test"])
    assert [check.id for check in selected] == ["backend-test"]

    with pytest.raises(ConfigError, match="did not match"):
        select_checks(checks, layers=["frontend"], check_ids=["backend-test"])


def test_unknown_filters_are_rejected(tmp_path: Path) -> None:
    _, checks = _catalog(tmp_path)

    with pytest.raises(ConfigError, match="Unknown layer"):
        select_checks(checks, layers=["mobile"])

    with pytest.raises(ConfigError, match="Unknown check id"):
        select_checks(checks, check_ids=["deploy"])
