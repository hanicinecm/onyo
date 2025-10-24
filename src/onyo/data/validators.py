"""Custom validators for the recipe and ingredient data models."""

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any


def freeze_mapping(value: Mapping[Any, Any] | None) -> Mapping[Any, Any] | None:
    """Turn any mapping into an immutable mapping."""
    if value is None:
        return None
    return MappingProxyType(dict(value))


def resolve_path(path: Path | None) -> Path | None:
    """Convert a path to its absolute form."""
    if path is None:
        return None
    return path.resolve()
