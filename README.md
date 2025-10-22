# ONYO

My personal recipe manager.

## Configuration

onyo reads its settings from a YAML file located at
`~/.config/onyo/onyo-config.yaml`. The configuration controls where the
application finds the recipe repository and will expand to cover additional
options over time.

### First-time setup

1. Run the application (or invoke `onyo.config.get_config()` during development).
2. If the config file is missing, onyo creates the directory and writes a
   template that includes placeholder values such as `<SET PATH TO RECIPES>`.
3. The loader raises `ConfigurationFileMissingError` to halt startup. Edit the
   generated file and replace every placeholder with a valid value before
   retrying.

### Editing configuration

- `recipe_repo_path` must point to an existing directory containing the curated
  YAML recipes. The loader validates that the path exists and is a directory.
- Leave optional keys (future additions) unset to accept the documented default
  behaviour provided by the `Configuration` dataclass.
- Keep placeholder markers out of committed configs; if a placeholder reaches
  runtime the loader raises `PlaceholderConfigurationError`.

### Reloading at runtime

- Use `onyo.config.reload_config()` to refresh settings after editing the YAML
  file. Cached values are cleared and the new configuration replaces the
  previous instance.
- Consumers that only need the current configuration should call
  `onyo.config.get_config()`; the loader caches the parsed object and performs
  filesystem validation on demand.

## Development

- Run linting and formatting: `source .venv/bin/activate && ruff check --fix && ruff format`
- Execute the test suite: `source .venv/bin/activate && pytest`
