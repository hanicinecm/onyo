"""Integration-style tests for :mod:`onyo.config.loader`."""

from pathlib import Path

import pytest

from onyo.config import get_config as public_get_config
from onyo.config import reload_config as public_reload_config
from onyo.config.loader import (
    CONFIG_FILENAME,
    default_config_path,
    get_configuration,
    load_configuration,
    reload_configuration,
    render_template,
)
from onyo.config.models import (
    Configuration,
    ConfigurationFileMissingError,
    InvalidConfigurationError,
)


def test_default_config_path_points_to_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    expected = fake_home / ".config/onyo" / CONFIG_FILENAME
    assert default_config_path() == expected


def test_load_configuration_bootstraps_missing_file(tmp_path: Path) -> None:
    config_path = tmp_path / "onyo-config.yaml"

    with pytest.raises(ConfigurationFileMissingError, match="template was created"):
        load_configuration(config_path=config_path, ensure_paths=False)

    assert config_path.exists()
    content = config_path.read_text(encoding="utf-8")
    placeholder = Configuration.placeholders()["recipe_repo_path"]
    assert placeholder in content


def test_load_configuration_round_trip(tmp_path: Path) -> None:
    repo_path = tmp_path / "recipes"
    repo_path.mkdir()
    config_path = tmp_path / "onyo-config.yaml"
    config_path.write_text(f"recipe_repo_path: {repo_path}\n", encoding="utf-8")

    configuration = load_configuration(config_path=config_path)

    assert configuration.recipe_repo_path == repo_path


def test_load_configuration_path_validation(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing"
    config_path = tmp_path / "onyo-config.yaml"
    config_path.write_text(f"recipe_repo_path: {missing_path}\n", encoding="utf-8")

    with pytest.raises(InvalidConfigurationError, match="path does not exist"):
        load_configuration(config_path=config_path)


def test_load_configuration_requires_mapping(tmp_path: Path) -> None:
    config_path = tmp_path / "onyo-config.yaml"
    config_path.write_text("- item\n- other\n", encoding="utf-8")

    with pytest.raises(InvalidConfigurationError, match="mapping"):
        load_configuration(config_path=config_path, ensure_paths=False)


def test_get_configuration_caches_result(tmp_path: Path) -> None:
    repo_path = tmp_path / "recipes"
    repo_path.mkdir()
    config_path = tmp_path / "onyo-config.yaml"
    config_path.write_text(f"recipe_repo_path: {repo_path}\n", encoding="utf-8")

    first = get_configuration(config_path=config_path)
    second = get_configuration(config_path=config_path)

    assert first is second


def test_reload_configuration_refreshes_cache(tmp_path: Path) -> None:
    repo_path = tmp_path / "recipes"
    repo_path.mkdir()
    config_path = tmp_path / "onyo-config.yaml"
    config_path.write_text(f"recipe_repo_path: {repo_path}\n", encoding="utf-8")

    initial = get_configuration(config_path=config_path)
    assert initial.recipe_repo_path == repo_path

    new_repo_path = tmp_path / "recipes-new"
    new_repo_path.mkdir()
    config_path.write_text(f"recipe_repo_path: {new_repo_path}\n", encoding="utf-8")

    # Cache should still return the original configuration.
    cached = get_configuration(config_path=config_path)
    assert cached.recipe_repo_path == repo_path

    refreshed = reload_configuration(config_path=config_path)
    assert refreshed.recipe_repo_path == new_repo_path


def test_load_configuration_rejects_non_directory_path(tmp_path: Path) -> None:
    file_path = tmp_path / "not_directory"
    file_path.write_text("content", encoding="utf-8")
    config_path = tmp_path / "onyo-config.yaml"
    config_path.write_text(f"recipe_repo_path: {file_path}\n", encoding="utf-8")

    with pytest.raises(InvalidConfigurationError, match="must point to a directory"):
        load_configuration(config_path=config_path)


def test_public_api_wrappers_delegates_to_loader(tmp_path: Path) -> None:
    repo_path = tmp_path / "recipes"
    repo_path.mkdir()
    config_path = tmp_path / "onyo-config.yaml"
    config_path.write_text(f"recipe_repo_path: {repo_path}\n", encoding="utf-8")

    initial = public_get_config(config_path=config_path)
    assert initial.recipe_repo_path == repo_path

    new_repo_path = tmp_path / "recipes-updated"
    new_repo_path.mkdir()
    config_path.write_text(f"recipe_repo_path: {new_repo_path}\n", encoding="utf-8")

    refreshed = public_reload_config(config_path=config_path)
    assert refreshed.recipe_repo_path == new_repo_path


def test_render_template_includes_guidance() -> None:
    template = render_template()

    assert "Replace placeholder values" in template
    placeholder = Configuration.placeholders()["recipe_repo_path"]
    assert placeholder in template


def test_load_configuration_with_invalid_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "onyo-config.yaml"
    config_path.write_text("recipe_repo_path: [unbalanced\n", encoding="utf-8")

    with pytest.raises(InvalidConfigurationError, match="YAML parsing error"):
        load_configuration(config_path=config_path, ensure_paths=False)
