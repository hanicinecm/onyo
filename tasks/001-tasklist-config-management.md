# Task List for Feature Configuration Management

## Relevant Files

- `src/onyo/config/__init__.py` - Public access point for configuration loading and reloading utilities.
- `src/onyo/config/models.py` - Defines the strongly typed `Configuration` class with defaults and validation logic.
- `src/onyo/config/loader.py` - Handles reading YAML, applying defaults, error handling, and reload flows.
- `tests/test_config_models.py` - Unit tests for configuration model validation and defaults.
- `tests/test_config_loader.py` - Integration-style tests covering file creation, parsing, and reload behavior.
- `README.md` - Document configuration expectations and how to supply the config file.

## Tasks

- [x] 1 Define configuration schema and defaults within a dedicated `Configuration` class.
  - [x] 1.1 Create `src/onyo/config/models.py` with a `Configuration` dataclass or Pydantic model capturing required/optional fields and defaults.
  - [x] 1.2 Implement validation helpers on the model to cast types (e.g., `Path`) and detect placeholder values or missing data.
  - [x] 1.3 Document inline comments within the model describing each field, its default, and validation rules for future contributors.
- [ ] 2 Implement configuration loading pipeline with validation, error handling, and missing-file bootstrapping.
  - [ ] 2.1 Build `src/onyo/config/loader.py` to resolve the config path, create parent directories, and detect missing files.
  - [ ] 2.2 Add logic to render and write a starter YAML template when the config file is absent, using placeholders for required fields.
  - [ ] 2.3 Parse existing YAML safely, merge with defaults, instantiate the `Configuration` model, and surface descriptive exceptions for invalid entries.
  - [ ] 2.4 Provide optional runtime checks for filesystem paths (existence/readability) controlled via model flags or loader parameters.
- [ ] 3 Expose configuration access and refresh hooks for the rest of the application.
  - [ ] 3.1 Implement `get_config()` in `src/onyo/config/__init__.py` to cache and return the current configuration instance.
  - [ ] 3.2 Add a `reload_config()` (or similar) function that clears caches and re-runs the loader pipeline on demand.
  - [ ] 3.3 Ensure configuration functions integrate cleanly with future UI/CLI refresh triggers (document usage in docstrings).
- [ ] 4 Cover configuration logic with automated tests and developer documentation updates.
  - [ ] 4.1 Write unit tests for the `Configuration` model (`tests/test_config_models.py`) covering type casting, default application, and validation failures.
  - [ ] 4.2 Write integration tests for the loader (`tests/test_config_loader.py`) covering missing-file creation, successful load, reload behavior, and error reporting.
  - [ ] 4.3 Update `README.md` (or dedicated docs) with steps to locate/edit the config file, including guidance on handling placeholder values and errors.
