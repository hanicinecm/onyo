# ruff: noqa: D103, S101, SLF001

"""Unit tests for :mod:`onyo.config.models`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from onyo.config.models import (
    Configuration,
    ConfigurationFileMissingError,
    InvalidConfigurationError,
    MissingConfigurationError,
    PlaceholderConfigurationError,
)


def test_defaults_returns_copy() -> None:
    defaults = Configuration.defaults()
    defaults["recipe_repo_path"] = "mutated"

    fresh = Configuration.defaults()
    placeholder = Configuration.placeholders()["recipe_repo_path"]
    assert fresh["recipe_repo_path"] == placeholder


def test_placeholders_returns_copy() -> None:
    placeholders = Configuration.placeholders()
    placeholders["recipe_repo_path"] = "mutated"

    fresh = Configuration.placeholders()
    expected = Configuration.defaults()["recipe_repo_path"]
    assert fresh["recipe_repo_path"] == expected


def test_from_mapping_with_valid_path(tmp_path: Path) -> None:
    config = Configuration.from_mapping({"recipe_repo_path": str(tmp_path)})

    assert config.recipe_repo_path == tmp_path


def test_from_mapping_strips_whitespace(tmp_path: Path) -> None:
    raw_value = f" {tmp_path}  "
    config = Configuration.from_mapping({"recipe_repo_path": raw_value})

    assert config.recipe_repo_path == tmp_path


def test_from_mapping_with_placeholder_raises() -> None:
    with pytest.raises(PlaceholderConfigurationError):
        Configuration.from_mapping({})


def test_from_mapping_with_blank_value_raises() -> None:
    with pytest.raises(MissingConfigurationError):
        Configuration.from_mapping({"recipe_repo_path": "   "})


def test_from_mapping_with_uncoercible_value_raises() -> None:
    with pytest.raises(InvalidConfigurationError):
        Configuration.from_mapping({"recipe_repo_path": object()})


def test_validate_required_fields_raises_when_missing() -> None:
    with pytest.raises(MissingConfigurationError):
        Configuration._validate_required_fields({})


def test_coerce_recipe_repo_path_rejects_none() -> None:
    with pytest.raises(MissingConfigurationError):
        Configuration._coerce_recipe_repo_path(None)


def test_to_mapping_serialises_path(tmp_path: Path) -> None:
    config = Configuration(recipe_repo_path=tmp_path)

    mapping = config.to_mapping()
    assert mapping == {"recipe_repo_path": str(tmp_path)}


def test_configuration_file_missing_error_message(tmp_path: Path) -> None:
    error = ConfigurationFileMissingError(tmp_path)

    message = str(error)
    assert str(tmp_path) in message
    assert "template" in message.lower()
