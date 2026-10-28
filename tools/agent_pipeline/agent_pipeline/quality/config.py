"""Configuration loading and validation for the quality gate.

The committed defaults live in ``tools/agent_pipeline/pyproject.toml`` under
``[tool.agent_pipeline.quality]``. Unknown keys are rejected so a typo cannot
silently disable a threshold or a timeout.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

CONFIG_SECTION = ("tool", "agent_pipeline", "quality")
ROOT_KEYS = frozenset(
    {
        "schema_version",
        "output_dir",
        "default_timeout_seconds",
        "max_output_bytes",
        "thresholds",
        "timeouts",
        "security",
    }
)
THRESHOLD_KEYS = frozenset({"python_complexity", "typescript_complexity"})
SECURITY_KEYS = frozenset({"uv_audit", "pnpm_audit", "ruff_s"})
SECURITY_MODES = frozenset({"off", "optional", "required"})

DEFAULT_THRESHOLD = 10
DEFAULT_TIMEOUT_SECONDS = 600.0
DEFAULT_MAX_OUTPUT_BYTES = 65536
DEFAULT_OUTPUT_DIR = ".quality"


class ConfigError(Exception):
    """Raised when the quality configuration is missing or invalid."""


@dataclass(frozen=True)
class SecurityConfig:
    """Opt-in state for the security checks evaluated in issue #44."""

    uv_audit: str = "optional"
    pnpm_audit: str = "optional"
    ruff_s: str = "required"


@dataclass(frozen=True)
class QualityConfig:
    """Validated quality-gate configuration."""

    schema_version: int
    output_dir: str
    default_timeout_seconds: float
    max_output_bytes: int
    python_complexity: int
    typescript_complexity: int
    timeouts: Mapping[str, float]
    security: SecurityConfig
    source: Path


def find_repo_root(start: Path) -> Path:
    """Walk upwards until the repository markers are found.

    Falls back to ``start`` when the markers are absent, which keeps the
    library usable in tests and in isolated checkouts.
    """
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / "AGENTS.md").is_file() and (
            candidate / "tools" / "agent_pipeline" / "pyproject.toml"
        ).is_file():
            return candidate
    return current


def default_config_path(repo_root: Path) -> Path:
    """Return the committed configuration for a repository root."""
    return repo_root / "tools" / "agent_pipeline" / "pyproject.toml"


def _reject_unknown(
    table: Mapping[str, Any], allowed: frozenset[str], where: str
) -> None:
    unknown = sorted(set(table) - allowed)
    if unknown:
        raise ConfigError(
            f"Unknown key(s) in {where}: {', '.join(unknown)}. "
            f"Allowed keys: {', '.join(sorted(allowed))}."
        )


def _positive_number(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ConfigError(f"{where} must be a positive number, got {value!r}.")
    return float(value)


def _positive_int(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ConfigError(f"{where} must be a positive integer, got {value!r}.")
    return value


def _table(value: Any, where: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{where} must be a TOML table, got {type(value).__name__}.")
    return value


def _string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{where} must be a non-empty string, got {value!r}.")
    return value


def _security_mode(value: Any, where: str) -> str:
    mode = _string(value, where)
    if mode not in SECURITY_MODES:
        raise ConfigError(
            f"{where} must be one of {', '.join(sorted(SECURITY_MODES))}, got {mode!r}."
        )
    return mode


def load_config(path: Path) -> QualityConfig:
    """Read and validate a quality configuration file."""
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise ConfigError(f"Configuration file not found: {path}") from exc
    except OSError as exc:
        raise ConfigError(f"Could not read configuration file {path}: {exc}") from exc

    try:
        document = tomllib.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"Invalid TOML in {path}: {exc}") from exc

    section: Any = document
    for key in CONFIG_SECTION:
        if not isinstance(section, dict) or key not in section:
            raise ConfigError(
                f"Missing [{'.'.join(CONFIG_SECTION)}] section in {path}."
            )
        section = section[key]

    table = _table(section, "tool.agent_pipeline.quality")
    _reject_unknown(table, ROOT_KEYS, "tool.agent_pipeline.quality")

    schema_version = table.get("schema_version", SCHEMA_VERSION)
    if schema_version != SCHEMA_VERSION:
        raise ConfigError(
            "Unsupported schema_version "
            f"{schema_version!r}; this tool understands {SCHEMA_VERSION}."
        )

    output_dir = _string(
        table.get("output_dir", DEFAULT_OUTPUT_DIR),
        "tool.agent_pipeline.quality.output_dir",
    )
    default_timeout = _positive_number(
        table.get("default_timeout_seconds", DEFAULT_TIMEOUT_SECONDS),
        "tool.agent_pipeline.quality.default_timeout_seconds",
    )
    max_output_bytes = _positive_int(
        table.get("max_output_bytes", DEFAULT_MAX_OUTPUT_BYTES),
        "tool.agent_pipeline.quality.max_output_bytes",
    )

    thresholds = _table(
        table.get("thresholds", {}),
        "tool.agent_pipeline.quality.thresholds",
    )
    _reject_unknown(thresholds, THRESHOLD_KEYS, "quality.thresholds")
    python_complexity = _positive_int(
        thresholds.get("python_complexity", DEFAULT_THRESHOLD),
        "tool.agent_pipeline.quality.thresholds.python_complexity",
    )
    typescript_complexity = _positive_int(
        thresholds.get("typescript_complexity", DEFAULT_THRESHOLD),
        "tool.agent_pipeline.quality.thresholds.typescript_complexity",
    )

    timeouts = _table(
        table.get("timeouts", {}),
        "tool.agent_pipeline.quality.timeouts",
    )
    parsed_timeouts: dict[str, float] = {}
    for check_id, value in timeouts.items():
        parsed_timeouts[check_id] = _positive_number(
            value, f"tool.agent_pipeline.quality.timeouts.{check_id}"
        )

    security_table = _table(
        table.get("security", {}),
        "tool.agent_pipeline.quality.security",
    )
    _reject_unknown(security_table, SECURITY_KEYS, "quality.security")
    security = SecurityConfig(
        uv_audit=_security_mode(
            security_table.get("uv_audit", "optional"),
            "tool.agent_pipeline.quality.security.uv_audit",
        ),
        pnpm_audit=_security_mode(
            security_table.get("pnpm_audit", "optional"),
            "tool.agent_pipeline.quality.security.pnpm_audit",
        ),
        ruff_s=_security_mode(
            security_table.get("ruff_s", "required"),
            "tool.agent_pipeline.quality.security.ruff_s",
        ),
    )

    return QualityConfig(
        schema_version=SCHEMA_VERSION,
        output_dir=output_dir,
        default_timeout_seconds=default_timeout,
        max_output_bytes=max_output_bytes,
        python_complexity=python_complexity,
        typescript_complexity=typescript_complexity,
        timeouts=parsed_timeouts,
        security=security,
        source=path.resolve(),
    )


def apply_overrides(
    config: QualityConfig,
    *,
    timeouts: Mapping[str, float] | None = None,
    python_complexity: int | None = None,
    typescript_complexity: int | None = None,
    max_output_bytes: int | None = None,
) -> QualityConfig:
    """Return a copy of ``config`` with validated CLI overrides applied."""
    merged_timeouts = dict(config.timeouts)
    for check_id, value in (timeouts or {}).items():
        merged_timeouts[check_id] = _positive_number(value, f"--timeout {check_id}")
    return replace(
        config,
        timeouts=merged_timeouts,
        python_complexity=(
            config.python_complexity
            if python_complexity is None
            else _positive_int(python_complexity, "--python-complexity")
        ),
        typescript_complexity=(
            config.typescript_complexity
            if typescript_complexity is None
            else _positive_int(typescript_complexity, "--typescript-complexity")
        ),
        max_output_bytes=(
            config.max_output_bytes
            if max_output_bytes is None
            else _positive_int(max_output_bytes, "--max-output-bytes")
        ),
    )
