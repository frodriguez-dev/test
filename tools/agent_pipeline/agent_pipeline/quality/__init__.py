"""Quality-gate library and CLI.

Later issues can call :func:`run_quality` in-process; the CLI in
:mod:`agent_pipeline.quality.cli` wraps the same functions.
"""

from .checks import build_checks, select_checks
from .config import ConfigError, QualityConfig, load_config
from .models import (
    SCHEMA_VERSION,
    CheckResult,
    CheckSpec,
    GateReport,
    Layer,
    Status,
)
from .runner import collect_tool_versions, run_check, run_quality

__all__ = [
    "CheckResult",
    "CheckSpec",
    "ConfigError",
    "GateReport",
    "Layer",
    "QualityConfig",
    "SCHEMA_VERSION",
    "Status",
    "build_checks",
    "collect_tool_versions",
    "load_config",
    "run_check",
    "run_quality",
    "select_checks",
]
