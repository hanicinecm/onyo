"""Configuration package exposing helpers to load onyo settings.

Consumers should prefer :func:`get_config` for retrieving the cached configuration
object and :func:`reload_config` when changes on disk need to be applied immediately.
"""

from pathlib import Path

from .loader import (
    default_config_path,
    get_configuration,
    load_configuration,
    reload_configuration,
)
from .models import Configuration

__all__ = [
    "Configuration",
    "default_config_path",
    "get_config",
    "load_configuration",
    "reload_config",
]


def get_config(
    *,
    config_path: Path | None = None,
    ensure_paths: bool = True,
) -> Configuration:
    """Return the current configuration instance.

    Args:
        config_path: Optional override for the configuration file path. Most callers
            should rely on the default provided by :func:`default_config_path`.
        ensure_paths: When ``True`` (default), perform filesystem validation on path
            fields. UI or CLI refresh hooks can disable this in contexts where the path
            is already known to exist (e.g., when editing within a guided workflow).
    """
    return get_configuration(config_path=config_path, ensure_paths=ensure_paths)


def reload_config(
    *,
    config_path: Path | None = None,
    ensure_paths: bool = True,
) -> Configuration:
    """Reload the configuration from disk and update the cache.

    This helper is intended for refresh flows triggered by the UI or CLI, ensuring that
    subsequent calls to :func:`get_config` return the updated data without re-reading
    the file repeatedly.
    """
    return reload_configuration(config_path=config_path, ensure_paths=ensure_paths)
