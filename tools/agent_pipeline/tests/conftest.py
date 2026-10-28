"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import install_fake_tools, make_repo, prepend_path


@pytest.fixture
def fake_tools(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Put fake ``uv``, ``pnpm``, ``make``, and ``noisy`` executables on PATH."""
    bin_dir = install_fake_tools(tmp_path / "bin")
    prepend_path(monkeypatch, bin_dir)
    return bin_dir


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A minimal repository layout with a quality configuration."""
    return make_repo(tmp_path / "repo")
