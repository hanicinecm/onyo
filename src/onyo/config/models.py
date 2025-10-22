"""Typed configuration models for the onyo application.

This module defines the primary :class:`Configuration` class that the rest of the
application will consume. The class is responsible for exposing default values for
each configurable field and acts as the central source of truth for required
settings.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


class ConfigurationError(ValueError):
    """Base class for configuration-related validation errors."""


class MissingConfigurationError(ConfigurationError):
    """Raised when one or more required configuration values are absent."""

    def __init__(self, fields: Iterable[str]) -> None:
        """Initialise the error with the missing configuration field names.

        Args:
            fields: Names of configuration fields that are absent.
        """
        names = tuple(sorted(str(field) for field in fields))
        message = ", ".join(names)
        super().__init__(f"Missing required configuration fields: {message}")
        self.fields = names


class PlaceholderConfigurationError(ConfigurationError):
    """Raised when a required field still contains the placeholder value."""

    def __init__(self, field: str, config_path_hint: str) -> None:
        """Initialise the error with the offending field and where to fix it.

        Args:
            field: Name of the configuration field that contains the placeholder.
            config_path_hint: Human-readable hint directing the user to the config file.
        """
        base = f"Configuration field '{field}' still contains the placeholder value."
        guidance = f" Update {config_path_hint} with a valid value."
        super().__init__(base + guidance)
        self.field = field
        self.config_path_hint = config_path_hint


class InvalidConfigurationError(ConfigurationError):
    """Raised when a configuration value cannot be coerced to the expected type."""

    def __init__(self, field: str, reason: str) -> None:
        """Initialise the error with the field name and the failure reason.

        Args:
            field: Name of the configuration field with the invalid value.
            reason: Description of why the value is invalid.
        """
        super().__init__(f"Invalid value for configuration field '{field}': {reason}")
        self.field = field
        self.reason = reason


class ConfigurationFileMissingError(ConfigurationError):
    """Raised when the configuration file is absent and a template was generated."""

    def __init__(self, path: Path) -> None:
        """Initialise the error with the path to the missing configuration file.

        Args:
            path: Filesystem location where the configuration file is expected.
        """
        message = (
            f"No configuration file found at {path}. A template was created; update it "
            "with valid values before retrying."
        )
        super().__init__(message)
        self.path = path


@dataclass(slots=True)
class Configuration:
    """Strongly typed configuration values used by the onyo application.

    The class encapsulates the validated configuration surface that other parts of the
    system consume. Configuration data flows through the following stages:

    * `_PLACEHOLDERS` stores template values keyed by field name. Those placeholders
      are written into an auto-generated YAML file to highlight required inputs that
      the user must replace.
    * `_DEFAULTS` provides the baseline values merged with user-supplied data before
      validation. Defaults may reference placeholders (for required fields) or concrete
      runtime defaults (for optional settings in the future).
    * `_REQUIRED_FIELDS` enumerates the keys that must be present after defaults and
      overrides have been merged.
    * `from_mapping()` applies defaults, merges the incoming mapping, and performs the
      validation steps. Missing keys raise :class:`MissingConfigurationError`, fields
      that still contain placeholder values raise
      :class:`PlaceholderConfigurationError`, and values that cannot be coerced to the
      expected type raise :class:`InvalidConfigurationError`.

    Attributes:
        recipe_repo_path: Filesystem location of the external recipe repository. This
            value is required and must resolve to a valid directory on disk.
    """

    recipe_repo_path: Path

    # Placeholder values written to generated config files for required fields.
    _PLACEHOLDERS: ClassVar[dict[str, str]] = {
        "recipe_repo_path": "<SET PATH TO RECIPES>",
    }
    # Path hint surfaced in placeholder-related validation errors.
    CONFIG_PATH_HINT: ClassVar[str] = "~/.config/onyo/onyo-config.yaml"
    # Default values applied prior to overlaying user-provided configuration.
    _DEFAULTS: ClassVar[dict[str, Any]] = {
        "recipe_repo_path": _PLACEHOLDERS["recipe_repo_path"],
    }
    # Fields that must be present after defaults are merged with user overrides.
    _REQUIRED_FIELDS: ClassVar[set[str]] = {"recipe_repo_path"}

    @classmethod
    def defaults(cls) -> dict[str, Any]:
        """Return a shallow copy of default configuration values.

        Returns:
            dict[str, Any]: Copy of the default configuration values.
        """
        return dict(cls._DEFAULTS)

    @classmethod
    def required_fields(cls) -> set[str]:
        """Return the set of required configuration field names.

        Returns:
            set[str]: Required configuration field names.
        """
        return set(cls._REQUIRED_FIELDS)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> Configuration:
        """Construct a configuration from raw mapping data.

        Args:
            data: Mapping containing overrides for configuration fields.

        Returns:
            A validated :class:`Configuration` instance.

        Raises:
            MissingConfigurationError: A required field is missing.
            PlaceholderConfigurationError: A required field still uses the placeholder.
            InvalidConfigurationError: A field holds a value of the wrong type.
        """
        merged: dict[str, Any] = cls.defaults()
        merged.update(dict(data))
        cls._validate_required_fields(merged)
        recipe_repo_path = cls._coerce_recipe_repo_path(merged["recipe_repo_path"])
        return cls(recipe_repo_path=recipe_repo_path)

    def to_mapping(self) -> dict[str, Any]:
        """Serialise the configuration to a mapping compatible with YAML dumps.

        Returns:
            dict[str, Any]: Mapping representation of the configuration.
        """
        return {"recipe_repo_path": str(self.recipe_repo_path)}

    @classmethod
    def _validate_required_fields(cls, values: Mapping[str, Any]) -> None:
        """Ensure all required fields are present after defaults are applied.

        Args:
            values: Mapping containing configuration field values.

        Raises:
            MissingConfigurationError: Raised when any required field is absent.
        """
        missing = {name for name in cls.required_fields() if name not in values}
        if missing:
            raise MissingConfigurationError(missing)

    @classmethod
    def placeholders(cls) -> dict[str, str]:
        """Return a shallow copy of placeholder values keyed by field name.

        Returns:
            dict[str, str]: Mapping of field name to placeholder value.
        """
        return dict(cls._PLACEHOLDERS)

    @classmethod
    def _coerce_recipe_repo_path(cls, raw_value: object) -> Path:
        """Convert and validate the recipe repository path value.

        Args:
            raw_value: Raw configuration value to convert to a ``Path`` instance.

        Returns:
            Path: Expanded filesystem path for the recipe repository.

        Raises:
            MissingConfigurationError: Raised when the field is blank or absent.
            PlaceholderConfigurationError: Raised when the generated placeholder value
                has not been replaced with a real path.
            InvalidConfigurationError: Raised when the value cannot be converted to a
                :class:`~pathlib.Path` instance.
        """
        if raw_value is None:
            raise MissingConfigurationError({"recipe_repo_path"})

        if isinstance(raw_value, str):
            stripped = raw_value.strip()
            if stripped == "":
                raise MissingConfigurationError({"recipe_repo_path"})
            placeholder = cls._PLACEHOLDERS["recipe_repo_path"]
            if stripped == placeholder:
                field_name = "recipe_repo_path"
                raise PlaceholderConfigurationError(field_name, cls.CONFIG_PATH_HINT)
            return Path(stripped).expanduser()

        try:
            return Path(raw_value).expanduser()  # type: ignore[arg-type]
        except TypeError as exc:  # pragma: no cover - defensive guard
            field_name = "recipe_repo_path"
            reason = "must be coercible to a filesystem path"
            raise InvalidConfigurationError(field_name, reason) from exc
