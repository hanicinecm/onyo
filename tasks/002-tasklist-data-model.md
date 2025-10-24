# Task List for Feature Data Model

## Relevant Files

- `src/onyo/data/__init__.py` - Package init to expose data-layer APIs.
- `src/onyo/data/models.py` - Domain models for recipes, ingredients, and corpus snapshots.
- `src/onyo/data/loader.py` - Corpus loading, validation, and snapshot refresh logic.
- `src/onyo/data/naming.py` - Helpers for enforcing unique names and generating slugs.
- `src/onyo/data/errors.py` - Custom exceptions and validation report structures.
- `tests/data/conftest.py` - Shared fixtures for synthetic corpus setup.
- `tests/data/resources/` - Synthetic corpus YAML files exercised by loader tests.
- `tests/data/test_models.py` - Unit tests for domain models.
- `tests/data/test_loader.py` - Integration tests for loading and validation workflows.

## Tasks

- [x] 1 Establish synthetic corpus fixtures and shared testing utilities.
  - [x] 1.1 Create `tests/data/resources/ingredients` and `tests/data/resources/recipes` directories with representative YAML samples (valid cases, missing fields, duplicate names).
  - [x] 1.2 Add a `tests/data/conftest.py` fixture that copies the sample corpus into a temporary directory to support mutation-free tests.
  - [x] 1.3 Document fixture usage patterns within `tests/data/conftest.py` to guide future contributors.
- [ ] 2 Implement domain models alongside focused unit tests.
  - [x] 2.1 Introduce `src/onyo/data/models.py` with Pydantic models for `Recipe`, `RecipeIngredient`, `Ingredient`, `NutritionProfile`, and `CorpusSnapshot`.
  - [ ] 2.2 Implement all the custom validation for the model classes.
  - [ ] 2.3 Write unit tests in `tests/data/test_models.py` verifying model construction, optional fields, error handling on duplicates, and immutability guarantees.
- [ ] 3 Build name-handling and validation-report utilities with corresponding tests.
  - [ ] 3.1 Implement `src/onyo/data/errors.py` with domain exceptions and a `ValidationReport` structure that aggregates per-file issues.
  - [ ] 3.2 Add unit tests in `tests/data/test_models.py` (or dedicated test modules) covering naming utilities, duplicate detection, and validation report aggregation.
- [ ] 4 Develop the corpus loader service with incremental integration tests.
  - [ ] 4.1 Implement `src/onyo/data/loader.py` to traverse recipes and ingredients, instantiate models, and collect validation report entries.
  - [ ] 4.2 Ensure the loader handles missing ingredients by creating ephemeral entries and linking them without raising fatal errors.
  - [ ] 4.3 Add snapshot management to replace prior corpus data atomically on success and retain previous snapshots on fatal validation errors.
  - [ ] 4.4 Write integration tests in `tests/data/test_loader.py` covering successful loads, duplicate name failures, missing ingredient fallbacks, and validation report outputs.
