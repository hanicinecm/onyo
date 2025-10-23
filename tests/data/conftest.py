"""Shared test fixtures for :mod:`onyo.data`.

`resources_dir` yields the canonical sample corpus used across the data-model
tests so suites can inspect raw YAML without mutating it. `corpus_dir` provides
an isolated copy of that corpus inside the pytest temporary directory, ensuring
tests operate on writeable copies while leaving the fixtures pristine.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

RESOURCE_ROOT = Path(__file__).parent / "resources"


@pytest.fixture
def resources_dir() -> Path:
    """Return the path to the bundled sample corpus resources."""
    return RESOURCE_ROOT


@pytest.fixture
def corpus_dir(tmp_path: Path, resources_dir: Path) -> Path:
    """Return a copy of the sample corpus in a temporary directory."""
    destination = tmp_path / "corpus"
    destination.mkdir()
    for name in ("ingredients", "recipes"):
        source = resources_dir / name
        shutil.copytree(source, destination / name)
    return destination
