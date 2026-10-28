"""Shared fixtures and helpers for the tooling tests."""

from __future__ import annotations

import os
from pathlib import Path

from agent_pipeline.quality.models import CheckSpec, Layer

FAKE_UV = """#!/bin/sh
args="$*"
if [ "${FAKE_SLEEP_LINT:-0}" = "1" ]; then
  case "$args" in
    *"ruff check --color=never ."*) sleep 10 ;;
  esac
fi
if [ "${FAKE_FAIL_COMPLEXITY:-0}" = "1" ]; then
  case "$args" in
    *"select C901"*) echo "C901 fake complexity failure"; exit 1 ;;
  esac
fi
if [ "${FAKE_FAIL_PYTEST:-0}" = "1" ]; then
  case "$args" in
    *pytest*) echo "fake pytest failure"; exit 3 ;;
  esac
fi
echo "fake uv: $args"
exit 0
"""

FAKE_PNPM = """#!/bin/sh
case "${1:-}" in
  test)
    if [ "${FAKE_FAIL_FRONTEND_TEST:-0}" = "1" ]; then
      echo "fake frontend test failure"
      exit 3
    fi
    ;;
  lint)
    if [ "${FAKE_FAIL_FRONTEND_LINT:-0}" = "1" ]; then
      echo "fake frontend lint failure"
      exit 1
    fi
    ;;
  exec)
    if [ "${FAKE_FAIL_FRONTEND_COMPLEXITY:-0}" = "1" ]; then
      echo "fake frontend complexity failure"
      exit 1
    fi
    ;;
esac
echo "fake pnpm: $*"
exit 0
"""

FAKE_MAKE = """#!/bin/sh
case "${1:-}" in
  backend-test)
    if [ "${FAKE_FAIL_BACKEND_TEST:-0}" = "1" ]; then
      echo "fake backend test failure"
      exit 2
    fi
    echo "fake backend tests passed"
    ;;
  frontend-build)
    if [ "${FAKE_FAIL_FRONTEND_BUILD:-0}" = "1" ]; then
      echo "fake frontend build failure"
      exit 2
    fi
    echo "fake frontend build passed"
    ;;
  *)
    echo "fake make: unknown target $*"
    exit 2
    ;;
esac
exit 0
"""

NOISY = """#!/bin/sh
i=0
while [ "$i" -lt 200 ]; do
  echo "0123456789012345678901234567890123456789"
  i=$((i + 1))
done
exit 0
"""

DEFINITELY_MISSING = "agent-pipeline-test-tool-that-does-not-exist"


def write_executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def install_fake_tools(bin_dir: Path) -> Path:
    bin_dir.mkdir(parents=True, exist_ok=True)
    write_executable(bin_dir / "uv", FAKE_UV)
    write_executable(bin_dir / "pnpm", FAKE_PNPM)
    write_executable(bin_dir / "make", FAKE_MAKE)
    write_executable(bin_dir / "noisy", NOISY)
    return bin_dir


CONFIG_TEMPLATE = """\
[tool.agent_pipeline.quality]
schema_version = 1
output_dir = ".quality"
default_timeout_seconds = 5
max_output_bytes = 4096
{extra_root}

[tool.agent_pipeline.quality.thresholds]
python_complexity = 10
typescript_complexity = 10

[tool.agent_pipeline.quality.timeouts]
backend-lint = 5
backend-format = 5
backend-typecheck = 5
backend-test = 5
frontend-typecheck = 5
frontend-lint = 5
frontend-format = 5
frontend-test = 5
frontend-build = 5
backend-complexity = 5
frontend-complexity = 5
python-security = 5
uv-audit = 5
pnpm-audit = 5
{extra_timeouts}

[tool.agent_pipeline.quality.security]
uv_audit = "{uv_audit}"
pnpm_audit = "{pnpm_audit}"
ruff_s = "{ruff_s}"
"""


def write_quality_config(
    path: Path,
    *,
    extra_root: str = "",
    extra_timeouts: str = "",
    uv_audit: str = "optional",
    pnpm_audit: str = "optional",
    ruff_s: str = "required",
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        CONFIG_TEMPLATE.format(
            extra_root=extra_root,
            extra_timeouts=extra_timeouts,
            uv_audit=uv_audit,
            pnpm_audit=pnpm_audit,
            ruff_s=ruff_s,
        ),
        encoding="utf-8",
    )
    return path


def make_repo(root: Path) -> Path:
    (root / "backend").mkdir(parents=True, exist_ok=True)
    (root / "frontend").mkdir(parents=True, exist_ok=True)
    (root / "AGENTS.md").write_text("test repository\n", encoding="utf-8")
    write_quality_config(root / "tools" / "agent_pipeline" / "pyproject.toml")
    return root


def make_spec(
    working_directory: Path,
    command: tuple[str, ...],
    *,
    check_id: str = "fake-check",
    required: bool = True,
    timeout_seconds: float = 5.0,
    skip_reason: str | None = None,
) -> CheckSpec:
    return CheckSpec(
        id=check_id,
        layer=Layer.BACKEND,
        description="fake check",
        command=command,
        working_directory=working_directory,
        required=required,
        timeout_seconds=timeout_seconds,
        skip_reason=skip_reason,
    )


def prepend_path(monkeypatch, bin_dir: Path) -> None:
    monkeypatch.setenv(
        "PATH",
        str(bin_dir) + os.pathsep + os.environ.get("PATH", ""),
    )
