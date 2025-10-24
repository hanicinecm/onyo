"""Unit tests for :mod:`onyo.config.models`."""

from pathlib import Path

import pytest

from onyo.config.models import (
    Configuration,
    ConfigurationFileMissingError,
    InvalidConfigurationError,
    MissingConfigurationError,
    PlaceholderConfigurationError,
)


def test_defaults_returns_copy() -> None:
    """Return a fresh defaults mapping on every call."""
    defaults = Configuration.defaults()
    defaults["recipe_repo_path"] = "mutated"

    fresh = Configuration.defaults()
    placeholder = Configuration.placeholders()["recipe_repo_path"]
    assert fresh["recipe_repo_path"] == placeholder


def test_placeholders_returns_copy() -> None:
    """Return a fresh placeholders mapping on every call."""
    placeholders = Configuration.placeholders()
    placeholders["recipe_repo_path"] = "mutated"

    fresh = Configuration.placeholders()
    expected = Configuration.defaults()["recipe_repo_path"]
    assert fresh["recipe_repo_path"] == expected


def test_from_mapping_with_valid_path(tmp_path: Path) -> None:
    """Coerce string paths from mappings into Path objects."""
    config = Configuration.from_mapping({"recipe_repo_path": str(tmp_path)})

    assert config.recipe_repo_path == tmp_path


def test_from_mapping_strips_whitespace(tmp_path: Path) -> None:
    """Strip surrounding whitespace when parsing mapping values."""
    raw_value = f" {tmp_path}  "
    config = Configuration.from_mapping({"recipe_repo_path": raw_value})

    assert config.recipe_repo_path == tmp_path


def test_from_mapping_with_placeholder_raises() -> None:
    """Raise when placeholder values are left unchanged."""
    with pytest.raises(PlaceholderConfigurationError):
        Configuration.from_mapping({})


def test_from_mapping_with_blank_value_raises() -> None:
    """Raise when mapping values are blank strings."""
    with pytest.raises(MissingConfigurationError):
        Configuration.from_mapping({"recipe_repo_path": "   "})


def test_from_mapping_with_uncoercible_value_raises() -> None:
    """Raise when mapping values cannot be coerced to paths."""
    with pytest.raises(InvalidConfigurationError):
        Configuration.from_mapping({"recipe_repo_path": object()})


def test_validate_required_fields_raises_when_missing() -> None:
    """Raise when required fields are missing from mapping."""
    with pytest.raises(MissingConfigurationError):
        Configuration._validate_required_fields({})


def test_coerce_recipe_repo_path_rejects_none() -> None:
    """Reject None values when coercing recipe repo path."""
    with pytest.raises(MissingConfigurationError):
        Configuration._coerce_recipe_repo_path(None)


def test_to_mapping_serialises_path(tmp_path: Path) -> None:
    """Serialise configuration paths back to strings."""
    config = Configuration(recipe_repo_path=tmp_path)

    mapping = config.to_mapping()
    assert mapping == {"recipe_repo_path": str(tmp_path)}


def test_configuration_file_missing_error_message(tmp_path: Path) -> None:
    """Include helpful guidance in missing configuration errors."""
    error = ConfigurationFileMissingError(tmp_path)

    message = str(error)
    assert str(tmp_path) in message
    assert "template" in message.lower()
