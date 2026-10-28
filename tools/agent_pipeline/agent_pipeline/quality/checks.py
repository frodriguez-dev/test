"""Build the concrete check catalog from configuration.

Commands are argument vectors executed with ``shell=False``. Backend and
frontend work uses the canonical commands already documented in the repository:
the ``make`` targets for the test suite and build, and the ``pnpm`` scripts or
tool commands for everything else.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from pathlib import Path

from .config import ConfigError, QualityConfig
from .models import CheckSpec, Layer

LAYERS = tuple(layer.value for layer in Layer)


def _timeout(config: QualityConfig, check_id: str) -> float:
    return config.timeouts.get(check_id, config.default_timeout_seconds)


def _network_skip_reason(
    mode: str,
    *,
    security_network: bool,
    label: str,
) -> str | None:
    if mode == "off":
        return f"{label} is disabled in the quality configuration."
    if security_network:
        return None
    return (
        f"{label} needs network access and is opt-in; rerun with "
        "--security-network to execute it."
    )


def build_checks(
    config: QualityConfig,
    repo_root: Path,
    *,
    security_network: bool = False,
) -> list[CheckSpec]:
    """Return every check in deterministic execution order."""
    repo_root = repo_root.resolve()
    backend_dir = repo_root / "backend"
    frontend_dir = repo_root / "frontend"

    def spec(
        check_id: str,
        layer: Layer,
        description: str,
        command: Sequence[str],
        working_directory: Path,
        *,
        required: bool = True,
        skip_reason: str | None = None,
        network: bool = False,
    ) -> CheckSpec:
        return CheckSpec(
            id=check_id,
            layer=layer,
            description=description,
            command=tuple(command),
            working_directory=working_directory,
            required=required,
            timeout_seconds=_timeout(config, check_id),
            skip_reason=skip_reason,
            network=network,
        )

    py_complexity = config.python_complexity
    ts_complexity = config.typescript_complexity

    checks = [
        spec(
            "backend-lint",
            Layer.BACKEND,
            "Ruff lint for the backend (includes C901 and S rules).",
            ("uv", "run", "ruff", "check", "--color=never", "."),
            backend_dir,
        ),
        spec(
            "backend-format",
            Layer.BACKEND,
            "Ruff format check for the backend.",
            ("uv", "run", "ruff", "format", "--check", "--color=never", "."),
            backend_dir,
        ),
        spec(
            "backend-typecheck",
            Layer.BACKEND,
            "Mypy type check for the backend.",
            ("uv", "run", "mypy", "--no-color-output", "manage.py", "config", "apps"),
            backend_dir,
        ),
        spec(
            "backend-test",
            Layer.BACKEND,
            "Backend pytest suite through the existing make target.",
            ("make", "backend-test"),
            repo_root,
        ),
        spec(
            "frontend-typecheck",
            Layer.FRONTEND,
            "TypeScript project check.",
            ("pnpm", "typecheck"),
            frontend_dir,
        ),
        spec(
            "frontend-lint",
            Layer.FRONTEND,
            "ESLint for the frontend (includes the complexity rule).",
            ("pnpm", "lint"),
            frontend_dir,
        ),
        spec(
            "frontend-format",
            Layer.FRONTEND,
            "Prettier check for the frontend.",
            ("pnpm", "format:check"),
            frontend_dir,
        ),
        spec(
            "frontend-test",
            Layer.FRONTEND,
            "Vitest suite for the frontend.",
            ("pnpm", "test"),
            frontend_dir,
        ),
        spec(
            "frontend-build",
            Layer.FRONTEND,
            "Production build through the existing make target.",
            ("make", "frontend-build"),
            repo_root,
        ),
        spec(
            "backend-complexity",
            Layer.COMPLEXITY,
            f"Ruff C901 with maximum complexity {py_complexity}.",
            (
                "uv",
                "run",
                "ruff",
                "check",
                "--select",
                "C901",
                "--config",
                f"lint.mccabe.max-complexity={py_complexity}",
                "--color=never",
                ".",
            ),
            backend_dir,
        ),
        spec(
            "frontend-complexity",
            Layer.COMPLEXITY,
            f"ESLint core complexity with maximum {ts_complexity}.",
            (
                "pnpm",
                "exec",
                "eslint",
                ".",
                "--rule",
                json.dumps({"complexity": ["error", ts_complexity]}),
            ),
            frontend_dir,
        ),
        spec(
            "python-security",
            Layer.SECURITY,
            "Ruff S (bandit) security rules for the backend.",
            ("uv", "run", "ruff", "check", "--select", "S", "--color=never", "."),
            backend_dir,
            required=True,
            skip_reason=(
                "Ruff S security rules are disabled in the quality "
                "configuration; this required check cannot be skipped."
                if config.security.ruff_s == "off"
                else None
            ),
        ),
        spec(
            "uv-audit",
            Layer.SECURITY,
            "Audit Python dependencies with uv audit (network).",
            ("uv", "audit", "--locked"),
            backend_dir,
            required=config.security.uv_audit == "required",
            skip_reason=_network_skip_reason(
                config.security.uv_audit,
                security_network=security_network,
                label="uv audit",
            ),
            network=True,
        ),
        spec(
            "pnpm-audit",
            Layer.SECURITY,
            "Audit Node dependencies with pnpm audit (network).",
            ("pnpm", "audit"),
            frontend_dir,
            required=config.security.pnpm_audit == "required",
            skip_reason=_network_skip_reason(
                config.security.pnpm_audit,
                security_network=security_network,
                label="pnpm audit",
            ),
            network=True,
        ),
    ]

    known_ids = {check.id for check in checks}
    unknown_timeouts = sorted(set(config.timeouts) - known_ids)
    if unknown_timeouts:
        raise ConfigError(
            "Unknown check id(s) in quality.timeouts: "
            f"{', '.join(unknown_timeouts)}. "
            f"Known ids: {', '.join(sorted(known_ids))}."
        )
    return checks


def select_checks(
    checks: Iterable[CheckSpec],
    *,
    layers: Sequence[str] | None = None,
    check_ids: Sequence[str] | None = None,
) -> list[CheckSpec]:
    """Filter the catalog by layer and/or check id, preserving order."""
    catalog = list(checks)
    known_layers = {check.layer.value for check in catalog}
    known_ids = {check.id for check in catalog}

    requested_layers = list(layers or ())
    requested_ids = list(check_ids or ())
    unknown_layers = sorted(set(requested_layers) - known_layers)
    if unknown_layers:
        raise ConfigError(
            f"Unknown layer(s): {', '.join(unknown_layers)}. "
            f"Known layers: {', '.join(sorted(known_layers))}."
        )
    unknown_ids = sorted(set(requested_ids) - known_ids)
    if unknown_ids:
        raise ConfigError(
            f"Unknown check id(s): {', '.join(unknown_ids)}. "
            f"Known ids: {', '.join(sorted(known_ids))}."
        )

    selected = [
        check
        for check in catalog
        if (not requested_layers or check.layer.value in requested_layers)
        and (not requested_ids or check.id in requested_ids)
    ]
    if not selected:
        raise ConfigError("The selection did not match any quality check.")
    return selected
