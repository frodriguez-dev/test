"""CLI for the local quality gate."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .checks import LAYERS, build_checks, select_checks
from .config import (
    ConfigError,
    QualityConfig,
    apply_overrides,
    default_config_path,
    find_repo_root,
    load_config,
)
from .models import SCHEMA_VERSION, CheckSpec, Status
from .report import render_human, report_to_json, write_report
from .runner import collect_tool_versions, run_quality


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m agent_pipeline",
        description="Repository tooling for the local agent pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    quality = subparsers.add_parser(
        "quality",
        help="Run the local quality gate.",
        description=(
            "Run backend, frontend, complexity, and security checks and "
            "report a stable result."
        ),
    )
    quality.add_argument(
        "--layer",
        action="append",
        choices=LAYERS,
        help="Run only this layer; repeat to select several layers.",
    )
    quality.add_argument(
        "--check",
        action="append",
        dest="check_ids",
        help="Run only this check id; repeat to select several checks.",
    )
    quality.add_argument(
        "--config",
        type=Path,
        help=(
            "Quality configuration file (default: tools/agent_pipeline/pyproject.toml)."
        ),
    )
    quality.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root (default: discovered from the current directory).",
    )
    quality.add_argument(
        "--json",
        action="store_true",
        help="Print the JSON report to stdout instead of the human summary.",
    )
    quality.add_argument(
        "--output",
        type=Path,
        help="Write the JSON report to this path (default: <output_dir>/quality.json).",
    )
    quality.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after the first required failure or error.",
    )
    quality.add_argument(
        "--security-network",
        action="store_true",
        help="Run the opt-in network-dependent security checks.",
    )
    quality.add_argument(
        "--timeout",
        action="append",
        default=[],
        metavar="CHECK_ID=SECONDS",
        help="Override the timeout for one check; repeat as needed.",
    )
    quality.add_argument(
        "--python-complexity",
        type=int,
        help="Override the Ruff C901 maximum complexity.",
    )
    quality.add_argument(
        "--typescript-complexity",
        type=int,
        help="Override the ESLint core complexity maximum.",
    )
    quality.add_argument(
        "--max-output-bytes",
        type=int,
        help="Override the per-check output cap.",
    )
    quality.add_argument(
        "--list-checks",
        action="store_true",
        help="List the configured checks and exit without running them.",
    )
    return parser


def _parse_timeouts(values: Sequence[str]) -> dict[str, float]:
    parsed: dict[str, float] = {}
    for value in values:
        if "=" not in value:
            raise ConfigError(f"--timeout expects CHECK_ID=SECONDS, got {value!r}.")
        check_id, raw_seconds = value.split("=", 1)
        check_id = check_id.strip()
        if not check_id:
            raise ConfigError(f"--timeout is missing a check id: {value!r}.")
        try:
            seconds = float(raw_seconds)
        except ValueError as exc:
            raise ConfigError(
                f"--timeout {check_id} expects a number, got {raw_seconds!r}."
            ) from exc
        if seconds <= 0:
            raise ConfigError(
                f"--timeout {check_id} must be positive, got {seconds:g}."
            )
        parsed[check_id] = seconds
    return parsed


def _resolve(args: argparse.Namespace) -> tuple[Path, QualityConfig]:
    repo_root = (
        args.repo_root.resolve()
        if args.repo_root is not None
        else find_repo_root(Path.cwd())
    )
    config_path = (
        args.config if args.config is not None else default_config_path(repo_root)
    )
    config = load_config(config_path)
    config = apply_overrides(
        config,
        timeouts=_parse_timeouts(args.timeout),
        python_complexity=args.python_complexity,
        typescript_complexity=args.typescript_complexity,
        max_output_bytes=args.max_output_bytes,
    )
    return repo_root, config


def _print_checks(checks: Sequence[CheckSpec]) -> None:
    headers = ("LAYER", "CHECK", "REQUIRED", "TIMEOUT", "DESCRIPTION")
    rows = [
        (
            check.layer.value,
            check.id,
            "yes" if check.required else "no",
            f"{check.timeout_seconds:g}s",
            check.description,
        )
        for check in checks
    ]
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    print(
        "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers))
    )
    for row in rows:
        print("  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return the process exit code."""
    parser = _parser()
    args = parser.parse_args(argv)

    try:
        repo_root, config = _resolve(args)
        checks = build_checks(
            config,
            repo_root,
            security_network=args.security_network,
        )
        checks = select_checks(
            checks,
            layers=args.layer,
            check_ids=args.check_ids,
        )
        if args.list_checks:
            _print_checks(checks)
            return 0

        output_dir = repo_root / config.output_dir
        report_path = (
            args.output.resolve()
            if args.output is not None
            else output_dir / "quality.json"
        )
        report = run_quality(
            checks,
            repo_root=repo_root,
            log_dir=output_dir / "logs",
            max_output_bytes=config.max_output_bytes,
            fail_fast=args.fail_fast,
            tool_versions=collect_tool_versions(),
        )
        write_report(report, report_path)

        if args.json:
            sys.stdout.write(report_to_json(report))
        else:
            sys.stdout.write(
                render_human(report, repo_root=repo_root, report_path=report_path)
            )
        return report.exit_code
    except ConfigError as exc:
        message = f"quality: configuration error: {exc}"
        if args.json:
            error_document = {
                "schema_version": SCHEMA_VERSION,
                "status": Status.ERROR.value,
                "exit_code": 2,
                "error": str(exc),
            }
            sys.stdout.write(json.dumps(error_document, indent=2) + "\n")
        print(message, file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("quality: interrupted", file=sys.stderr)
        return 2
