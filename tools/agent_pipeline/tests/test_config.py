"""Configuration loading, validation, and override behavior."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from agent_pipeline.quality.checks import build_checks
from agent_pipeline.quality.config import (
    ConfigError,
    apply_overrides,
    default_config_path,
    find_repo_root,
    load_config,
)

from tests.support import make_repo, write_quality_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMITTED_CONFIG = PROJECT_ROOT / "pyproject.toml"


def test_committed_config_loads() -> None:
    config = load_config(COMMITTED_CONFIG)

    assert config.schema_version == 1
    assert config.output_dir == ".quality"
    assert config.python_complexity == 10
    assert config.typescript_complexity == 10
    assert config.max_output_bytes == 65536
    assert config.security.uv_audit == "optional"
    assert config.security.pnpm_audit == "optional"
    assert config.security.ruff_s == "required"
    assert config.timeouts["backend-test"] == 900


def test_find_repo_root_and_default_config(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")

    assert find_repo_root(repo / "backend") == repo.resolve()
    assert default_config_path(repo) == repo / "tools/agent_pipeline/pyproject.toml"


def test_unknown_root_key_is_rejected(tmp_path: Path) -> None:
    path = write_quality_config(
        tmp_path / "quality.toml",
        extra_root="made_up_key = true",
    )

    with pytest.raises(ConfigError, match="Unknown key"):
        load_config(path)


def test_unknown_threshold_key_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "quality.toml"
    path.write_text(
        """
[tool.agent_pipeline.quality.thresholds]
python_complexity = 10
ruby_complexity = 3
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="ruby_complexity"):
        load_config(path)


def test_invalid_schema_version_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "quality.toml"
    path.write_text(
        """
[tool.agent_pipeline.quality]
schema_version = 99
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="Unsupported schema_version"):
        load_config(path)


def test_invalid_security_mode_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "quality.toml"
    path.write_text(
        """
[tool.agent_pipeline.quality.security]
uv_audit = "always"
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="uv_audit"):
        load_config(path)


def test_non_positive_timeout_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "quality.toml"
    path.write_text(
        """
[tool.agent_pipeline.quality.timeouts]
backend-lint = 0
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="positive"):
        load_config(path)


def test_missing_config_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "missing.toml")


def test_invalid_toml_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "quality.toml"
    path.write_text("[tool.agent_pipeline.quality\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="Invalid TOML"):
        load_config(path)


def test_unknown_timeout_check_id_is_rejected(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    path = write_quality_config(
        tmp_path / "quality.toml",
        extra_timeouts="not-a-check = 3",
    )
    config = load_config(path)

    with pytest.raises(ConfigError, match="not-a-check"):
        build_checks(config, repo)


def test_overrides_replace_values() -> None:
    config = load_config(COMMITTED_CONFIG)

    updated = apply_overrides(
        config,
        timeouts={"backend-lint": 7},
        python_complexity=4,
        typescript_complexity=5,
        max_output_bytes=1024,
    )

    assert updated.timeouts["backend-lint"] == 7
    assert updated.python_complexity == 4
    assert updated.typescript_complexity == 5
    assert updated.max_output_bytes == 1024
    # The original object is not mutated.
    assert config.timeouts["backend-lint"] == 180


def test_invalid_override_is_rejected() -> None:
    config = load_config(COMMITTED_CONFIG)

    with pytest.raises(ConfigError, match="positive"):
        apply_overrides(config, python_complexity=0)

    with pytest.raises(ConfigError, match="positive"):
        apply_overrides(config, timeouts={"backend-lint": 0})


def test_replace_keeps_configuration_immutable() -> None:
    config = load_config(COMMITTED_CONFIG)
    updated = replace(config, output_dir="reports")

    assert config.output_dir == ".quality"
    assert updated.output_dir == "reports"
    assert updated.source == config.source
