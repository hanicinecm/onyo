"""Custom validators for the Recipe and Ingredient Data models."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any


def freeze_mapping(value: Mapping[Any, Any] | None) -> Mapping[Any, Any] | None:
    """Turn any mapping into an immutable mapping."""
    if value is None:
        return None
    return MappingProxyType(dict(value))
