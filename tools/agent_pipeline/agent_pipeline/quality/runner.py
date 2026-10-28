"""Execute checks and aggregate them into a gate report."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

from .models import (
    CheckResult,
    CheckSpec,
    GateReport,
    Status,
    evaluate_gate,
)

# Deterministic, non-interactive environment for every child process. Secrets
# are inherited when a tool genuinely needs them (for example database
# credentials) but are never logged or included in reports.
BASE_ENV = {
    "CI": "1",
    "NO_COLOR": "1",
    "FORCE_COLOR": "0",
    "CLICOLOR": "0",
    "CLICOLOR_FORCE": "0",
    "PY_COLORS": "0",
    "TERM": "dumb",
    "PYTHONUNBUFFERED": "1",
    "UV_NO_PROGRESS": "1",
    "GIT_TERMINAL_PROMPT": "0",
}

# A parent `uv run --project tools/agent_pipeline` exports its virtualenv.
# Child projects must select their own environment, so drop these before
# starting a check.
DROP_ENV = ("VIRTUAL_ENV", "VIRTUAL_ENV_PROMPT", "PYTHONHOME")

TOOL_PROBES = {
    "uv": ("uv", "--version"),
    "pnpm": ("pnpm", "--version"),
    "node": ("node", "--version"),
    "make": ("make", "--version"),
}


def _child_env() -> dict[str, str]:
    env = os.environ.copy()
    for name in DROP_ENV:
        env.pop(name, None)
    env.update(BASE_ENV)
    return env


def collect_tool_versions() -> dict[str, str]:
    """Best-effort versions of the tools the gate may call.

    Missing tools are omitted instead of failing the gate, because the check
    that needs them reports a precise ``ERROR`` on its own.
    """
    env = _child_env()
    versions = {
        "python": (
            f"{sys.version_info.major}.{sys.version_info.minor}."
            f"{sys.version_info.micro}"
        )
    }
    for name, command in TOOL_PROBES.items():
        try:
            completed = subprocess.run(
                list(command),
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=5,
                env=env,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if completed.returncode != 0:
            continue
        lines = (completed.stdout or completed.stderr).strip().splitlines()
        if lines:
            versions[name] = lines[0].strip()
    return versions


TRUNCATION_TEMPLATE = (
    "\n[... output truncated: kept first {head} and last {tail} of {total} "
    "bytes (limit {limit}). ...]\n"
)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def truncate_output(data: bytes, limit: int) -> str:
    """Decode captured output and cap it with an explicit marker.

    The head and the tail are kept because failures usually explain themselves
    at the end of the stream, while the head identifies the command phase.
    """
    text = data.decode("utf-8", errors="replace")
    if len(data) <= limit:
        return text
    head_size = max(1, limit // 4)
    tail_size = max(1, limit - head_size)
    marker = TRUNCATION_TEMPLATE.format(
        head=head_size, tail=tail_size, total=len(data), limit=limit
    )
    head = data[:head_size].decode("utf-8", errors="replace")
    tail = data[-tail_size:].decode("utf-8", errors="replace")
    return f"{head}{marker}{tail}"


def _kill_process_group(process: subprocess.Popen[bytes]) -> None:
    """Terminate the child and every process it spawned."""
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        process.kill()


def _safe_log_name(check_id: str) -> str:
    safe = "".join(
        character if character.isalnum() or character in "-_." else "_"
        for character in check_id
    )
    return f"{safe or 'check'}.log"


def _relative_to(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def run_check(
    spec: CheckSpec,
    *,
    log_dir: Path,
    repo_root: Path,
    max_output_bytes: int,
) -> CheckResult:
    """Run one check without a shell and capture its combined output."""
    started = time.monotonic()
    if spec.skip_reason:
        status = Status.ERROR if spec.required else Status.SKIP
        prefix = "Required check skipped" if spec.required else "Skipped"
        return CheckResult(
            id=spec.id,
            layer=spec.layer,
            command=spec.command,
            working_directory=spec.working_directory,
            required=spec.required,
            status=status,
            exit_code=None,
            duration_seconds=0.0,
            summary=f"{prefix}: {spec.skip_reason}",
        )

    env = _child_env()
    env.update(spec.env)

    try:
        process = subprocess.Popen(
            list(spec.command),
            cwd=spec.working_directory,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except FileNotFoundError:
        duration = round(time.monotonic() - started, 3)
        return CheckResult(
            id=spec.id,
            layer=spec.layer,
            command=spec.command,
            working_directory=spec.working_directory,
            required=spec.required,
            status=Status.ERROR,
            exit_code=None,
            duration_seconds=duration,
            summary=f"Executable not found: {spec.command[0]}",
        )
    except OSError as exc:
        duration = round(time.monotonic() - started, 3)
        return CheckResult(
            id=spec.id,
            layer=spec.layer,
            command=spec.command,
            working_directory=spec.working_directory,
            required=spec.required,
            status=Status.ERROR,
            exit_code=None,
            duration_seconds=duration,
            summary=f"Could not start command: {exc}",
        )

    timed_out = False
    try:
        output, _ = process.communicate(timeout=spec.timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill_process_group(process)
        output, _ = process.communicate()

    duration = round(time.monotonic() - started, 3)
    truncated = truncate_output(output or b"", max_output_bytes)

    output_path: str | None = None
    if truncated:
        log_dir.mkdir(parents=True, exist_ok=True)
        artifact = log_dir / _safe_log_name(spec.id)
        artifact.write_text(truncated, encoding="utf-8")
        output_path = _relative_to(artifact, repo_root)

    if timed_out:
        return CheckResult(
            id=spec.id,
            layer=spec.layer,
            command=spec.command,
            working_directory=spec.working_directory,
            required=spec.required,
            status=Status.ERROR,
            exit_code=process.returncode,
            duration_seconds=duration,
            summary=(
                f"Timed out after {spec.timeout_seconds:g}s; "
                "the process group was terminated."
            ),
            output_path=output_path,
        )

    exit_code = process.returncode
    if exit_code == 0:
        return CheckResult(
            id=spec.id,
            layer=spec.layer,
            command=spec.command,
            working_directory=spec.working_directory,
            required=spec.required,
            status=Status.PASS,
            exit_code=0,
            duration_seconds=duration,
            summary="Command completed successfully.",
            output_path=output_path,
        )

    return CheckResult(
        id=spec.id,
        layer=spec.layer,
        command=spec.command,
        working_directory=spec.working_directory,
        required=spec.required,
        status=Status.FAIL,
        exit_code=exit_code,
        duration_seconds=duration,
        summary=f"Command exited with code {exit_code}.",
        output_path=output_path,
    )


def _not_run_result(
    spec: CheckSpec,
    *,
    stopped_by: str,
) -> CheckResult:
    return CheckResult(
        id=spec.id,
        layer=spec.layer,
        command=spec.command,
        working_directory=spec.working_directory,
        required=spec.required,
        status=Status.SKIP,
        exit_code=None,
        duration_seconds=0.0,
        summary=(f"Not run because --fail-fast stopped the gate after {stopped_by}."),
    )


def run_checks(
    checks: Sequence[CheckSpec],
    *,
    repo_root: Path,
    log_dir: Path,
    max_output_bytes: int,
    fail_fast: bool = False,
) -> tuple[CheckResult, ...]:
    """Run checks sequentially and return their results."""
    results: list[CheckResult] = []
    for index, spec in enumerate(checks):
        result = run_check(
            spec,
            log_dir=log_dir,
            repo_root=repo_root,
            max_output_bytes=max_output_bytes,
        )
        results.append(result)
        if (
            fail_fast
            and result.required
            and result.status
            in {
                Status.FAIL,
                Status.ERROR,
            }
        ):
            results.extend(
                _not_run_result(remaining, stopped_by=spec.id)
                for remaining in checks[index + 1 :]
            )
            break
    return tuple(results)


def run_quality(
    checks: Iterable[CheckSpec],
    *,
    repo_root: Path,
    log_dir: Path,
    max_output_bytes: int,
    fail_fast: bool = False,
    tool_versions: Mapping[str, str] | None = None,
) -> GateReport:
    """Run the selected checks and evaluate the documented gate semantics."""
    started_at = _utc_now()
    started = time.monotonic()
    results = run_checks(
        tuple(checks),
        repo_root=repo_root,
        log_dir=log_dir,
        max_output_bytes=max_output_bytes,
        fail_fast=fail_fast,
    )
    duration = round(time.monotonic() - started, 3)
    status, exit_code = evaluate_gate(results)
    return GateReport(
        status=status,
        exit_code=exit_code,
        started_at=started_at,
        finished_at=_utc_now(),
        duration_seconds=duration,
        checks=results,
        tool_versions=dict(tool_versions or {}),
    )
