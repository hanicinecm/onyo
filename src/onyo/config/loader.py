"""Configuration loading utilities for the onyo application.

This module is responsible for locating the YAML configuration file, creating a
starter template when it is missing, parsing the file into a strongly typed
``Configuration`` instance, and exposing convenience helpers for caching and
reload flows.
"""

from pathlib import Path
from typing import Any

import yaml

from .models import (
    Configuration,
    ConfigurationFileMissingError,
    InvalidConfigurationError,
)

CONFIG_FILENAME = "onyo-config.yaml"
CONFIG_DIRNAME = ".config/onyo"

_CACHE: dict[str, Any] = {"configuration": None, "path": None}


def default_config_path() -> Path:
    """Return the default filesystem path to the configuration file.

    Returns:
        Path: Location of the configuration YAML file.
    """
    return Path.home() / CONFIG_DIRNAME / CONFIG_FILENAME


def get_configuration(
    config_path: Path | None = None,
    *,
    ensure_paths: bool = True,
) -> Configuration:
    """Return the cached configuration, loading it if necessary.

    Args:
        config_path: Optional override pointing to a specific configuration file.
        ensure_paths: When ``True`` (default), perform filesystem validation of path
            fields after loading.

    Returns:
        A cached or freshly loaded :class:`Configuration` instance.

    Raises:
        ConfigurationError: Propagated when loading or validation fails.
    """
    resolved_path = config_path or default_config_path()
    cached = _CACHE["configuration"]
    cached_path = _CACHE["path"]
    if cached is not None and resolved_path == cached_path:
        if ensure_paths:
            _validate_paths(cached)
        return cached

    configuration = load_configuration(
        config_path=resolved_path, ensure_paths=ensure_paths
    )
    _CACHE["configuration"] = configuration
    _CACHE["path"] = resolved_path
    return configuration


def reload_configuration(
    config_path: Path | None = None,
    *,
    ensure_paths: bool = True,
) -> Configuration:
    """Force a configuration reload, bypassing the cache.

    Args:
        config_path: Optional override pointing to a specific configuration file.
        ensure_paths: When ``True`` (default), perform filesystem validation after
            loading.

    Returns:
        Configuration: Freshly loaded configuration instance.
    """
    _clear_cache()
    return get_configuration(config_path=config_path, ensure_paths=ensure_paths)


def load_configuration(
    *,
    config_path: Path | None = None,
    ensure_paths: bool = True,
) -> Configuration:
    """Load and validate configuration data from disk.

    Args:
        config_path: Optional override pointing to a specific configuration file.
        ensure_paths: When ``True`` (default), perform filesystem validation after
            loading.

    Returns:
        Configuration: Validated configuration.

    Raises:
        ConfigurationError: Propagated when validation fails.
    """
    resolved_path = config_path or default_config_path()
    data = _read_or_bootstrap_config(resolved_path)
    configuration = Configuration.from_mapping(data)
    if ensure_paths:
        _validate_paths(configuration)
    return configuration


def render_template() -> str:
    """Return the YAML template content used for initial configuration files.

    Returns:
        str: YAML template populated with placeholder values and guidance comments.
    """
    defaults = Configuration.defaults()
    header = (
        "# onyo configuration file\n"
        "# Replace placeholder values (e.g., <SET PATH TO RECIPES>) before restarting\n"
        "# the application. Missing or placeholder values will prevent startup.\n"
        "#\n"
        "# Fields:\n"
        "#   recipe_repo_path: Absolute path to the root of your recipe repository.\n"
        "\n"
    )
    body = yaml.safe_dump(defaults, sort_keys=False)
    return header + body


def _read_or_bootstrap_config(config_path: Path) -> dict[str, Any]:
    """Read the configuration mapping, bootstrapping the file when absent.

    Args:
        config_path: Path to the configuration file.

    Returns:
        dict[str, Any]: Raw configuration mapping loaded from YAML.

    Raises:
        ConfigurationFileMissingError: Raised after writing a template because the
            configuration does not yet exist.
        InvalidConfigurationError: Raised when the YAML cannot be parsed or is not a
            mapping.
    """
    if not config_path.exists():
        _write_template(config_path)
        raise ConfigurationFileMissingError(config_path)

    content = config_path.read_text(encoding="utf-8")
    try:
        loaded = yaml.safe_load(content) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - parsing errors are rare
        field_name = "<root>"
        reason = f"YAML parsing error: {exc}"
        raise InvalidConfigurationError(field_name, reason) from exc

    if not isinstance(loaded, dict):
        field_name = "<root>"
        reason = "configuration must be a mapping of keys to values"
        raise InvalidConfigurationError(field_name, reason)

    return loaded


def _validate_paths(configuration: Configuration) -> None:
    """Perform filesystem checks for configuration values that represent paths.

    Args:
        configuration: Configuration instance to validate.

    Raises:
        InvalidConfigurationError: Raised when declared paths do not exist or lack the
            expected type.
    """
    repo_path = configuration.recipe_repo_path
    if not repo_path.exists():
        field_name = "recipe_repo_path"
        reason = f"path does not exist: {repo_path}"
        raise InvalidConfigurationError(field_name, reason)
    if not repo_path.is_dir():
        field_name = "recipe_repo_path"
        reason = f"path must point to a directory: {repo_path}"
        raise InvalidConfigurationError(field_name, reason)


def _write_template(config_path: Path) -> None:
    """Create parent directories as needed and write the starter template.

    Args:
        config_path: Target path where the template should be written.
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)
    template = render_template()
    config_path.write_text(template, encoding="utf-8")


def _clear_cache() -> None:
    """Clear the in-memory configuration cache."""
    _CACHE["configuration"] = None
    _CACHE["path"] = None


__all__ = [
    "CONFIG_DIRNAME",
    "CONFIG_FILENAME",
    "default_config_path",
    "get_configuration",
    "load_configuration",
    "reload_configuration",
    "render_template",
]
