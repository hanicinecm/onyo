# Feature PRD: Configuration Management

## 1. Feature Overview

Configuration Management equips onyo with a robust way to load, validate, and refresh application settings from a YAML file. At launch the primary need is to locate the external recipe repository, but the design must welcome future configuration options (e.g., UI preferences, optional paths) without major refactoring. This feature ensures the Raspberry Pi-hosted app can always find its data source, fail loudly when configuration is incomplete, and regenerate a starter config when none exists.

## 2. Goals & Non-Goals

Goals:

- Resolve the recipe repository path via a configuration system that supports defaults, overrides, and validation.
- Automatically create a skeleton config file with placeholder values when none exists.
- Surface meaningful exceptions for missing or invalid configuration entries, including guidance on how to fix them.
- Allow the running app to reload configuration on demand so future settings can apply without restart.

Non-Goals:

- Providing a UI for editing configuration values.
- Managing secrets, credentials, or remote storage endpoints.
- Supporting multiple configuration layers or user-specific overrides beyond the single YAML file.

## 3. User Impact & Flows

- **Personas impacted**: Martin (maintainer) and Alicja (consumer). Martin primarily interacts with configuration setup and maintenance.
- **Primary flow**: On first run, onyo looks for `~/.config/onyo/onyo-config.yaml`. If missing, it creates the file with explanatory placeholders, raises an exception indicating required fields must be filled, and halts startup. After Martin fills in the recipe repository path, a restart or manual reload picks up the value.
- **Reload flow**: When Martin triggers a manual “reload configuration” action (to be wired into the existing refresh mechanism), the system re-reads and re-validates the YAML, applying new settings or surfacing errors immediately.
- **Acceptance criteria**
  - Given a valid config file with all required values, onyo loads the configuration and exposes strongly typed settings to the rest of the app.
  - Given a missing config file, onyo writes a starter file with placeholders, raises an exception that clearly instructs the user to edit the file, and does not continue bootstrapping.
  - Given an invalid or incomplete config, onyo raises a descriptive exception detailing each issue (e.g., wrong type, missing key, nonexistent path if checks are enabled).

## 4. Requirements

### Functional

- Locate configuration at a hard-coded default path (`Path.home() / ".config/onyo/onyo-config.yaml"`); allow future override via environment variable or CLI flag (design hooks only, no implementation yet).
- Define a `Configuration` object (dataclass, Pydantic model, or similar) that declares default values, strongly-typed fields, and embedded validation rules (initial field: `recipe_repo_path: Path`, required, no default).
- Load YAML into an intermediate structure, merge with defaults, validate types, and ensure required fields are present.
- When config file is absent, create parent directories if needed, write a YAML template with placeholder markers (`TODO` or similar), then raise a `ConfigurationMissingError`.
- Provide helper functions to format validation errors (missing key, invalid type, unreadable path) into actionable messages.
- Expose configuration reload API (`load_configuration(force_reload: bool = False)`) that can re-parse the file and replace the in-memory `Configuration`.

### Non-Functional

- Ensure path resolution and file writes use `pathlib` and respect user permissions.
- Keep load-time performance acceptable on Raspberry Pi (single YAML file; negligible overhead).
- Maintain clear exception hierarchy for configuration errors (e.g., `ConfigurationError`, `ConfigurationMissingError`, `ConfigurationValidationError`).
- Avoid side effects beyond optional file creation—no logging/UI prompts beyond raised exceptions.

### Data & Schema Changes

- Represent the configuration schema directly in the `Configuration` class definition (type hints, validators, defaults) rather than an external Yamale schema.
- Document the config schema in-line within the repo (README or dedicated docs section) and mirror it in the generated template.
- No database migrations; the only filesystem artifacts are the YAML config file and any supporting documentation.

## 5. Experience Notes

- The generated YAML should include concise comments describing each field, its purpose, default behavior, and required status.
- Error messages should follow a consistent tone: direct, actionable (“Configuration error: `recipe_repo_path` is missing. Edit ~/.config/onyo/onyo-config.yaml and set it to an existing directory.”).
- Placeholder values in the auto-created file must be easily distinguishable (e.g., `<SET PATH TO RECIPES>`), enabling the validator to flag them as unmet requirements.

## 6. Technical Design

- **Modules**: Introduce `src/onyo/config/loader.py` (loading/validation) and `src/onyo/config/models.py` (Configuration dataclass or Pydantic model). Export a public `get_config()` helper from `src/onyo/config/__init__.py`.
- **Workflow**:
  1. Determine config path.
  2. If file missing, create directories, render template (using defaults + placeholders), write file, raise `ConfigurationMissingError`.
  3. Load YAML (use safe loader), feed data into the `Configuration` class for validation and type coercion.
  4. Apply defaults from the `Configuration` class, convert to strongly typed object (e.g., using dataclass factory or Pydantic for casting to `Path`, bool, etc.).
  5. Optionally (configurable flag) check that declared paths exist; collect any errors.
  6. Cache configuration and expose thread-safe access; provide explicit `reload()` that re-runs the pipeline.
- **Future-proofing**: Architect the `Configuration` model to accept nested sections (e.g., `ui`, `integration`, `paths`). Validation helpers should automatically flag new required fields with minimal code changes.
- **Dependencies**: Rely on standard library (`pathlib`, `yaml` via PyYAML) and whichever model approach is chosen (dataclasses + custom validators or Pydantic). No background threads or file watchers required.

## 7. Testing Strategy

- **Unit tests**
  - Validate successful load with a fully populated config.
  - Verify defaults apply when optional fields are omitted once they exist.
  - Confirm type casting (strings to `Path`, booleans, integers) and error messaging when casting fails.
  - Ensure missing config triggers file creation and raises `ConfigurationMissingError`.
  - Test invalid YAML and schema violations produce `ConfigurationValidationError` with detailed messages.
- **Integration tests**
  - End-to-end load using temporary directories to simulate home config path.
  - Reload behavior: modify config file, invoke reload, assert updated values propagate.
- **Edge cases**
  - Config path points to unreadable location (permissions) -> expect clear exception.
  - Placeholder values remain untouched -> validator detects and instructs user to update.
  - Concurrent reads (if future multi-thread use) rely on thread-safe caching—cover with lightweight tests if needed.
