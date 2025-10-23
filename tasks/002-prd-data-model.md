# Feature PRD: Data Model

## 1. Feature Overview

The Data Model feature establishes the in-memory representation of the recipe corpus and the validation logic that keeps it trustworthy. It introduces typed models for recipes, their ingredient usage, and the shared ingredient catalog, providing a single source of truth for the rest of the application. The feature ensures the clear-text YAML repository can be loaded into Python objects with rigorous model-based validation and actionable feedback when data issues arise.

This work resolves the current gap between the external YAML corpus and the rest of the codebase. Once complete, the NiceGUI UI, search layer, and future services will read from well-defined models that accurately mirror the corpus structure and relationships.

## 2. Goals & Non-Goals

- Deliver immutable Python domain classes for `Recipe`, `RecipeIngredient`, and `Ingredient`, ensuring recipe and ingredient names remain unique within the corpus.
- Provide code that loads the corpus from disk into those classes so future runtime entry points can call it during startup or manual refresh moments.
- Validate recipe and ingredient YAML by instantiating the data models directly, accumulating all errors per run without relying on external schema definitions.
- Surface validation outcomes through structured reports so downstream consumers understand when data failed to load and why.
- Prepare the models for downstream consumers (search, UI) without locking in those implementations.

Non-goals:

- Building search, filtering, or presentation logic (they will consume the models once available).
- Allowing write-back or mutation of the YAML corpus from the app.
- Introducing a persistence layer beyond the existing clear-text repository.

## 3. User Impact & Flows

- **Corpus load on startup/refresh**: When the loader is invoked (e.g., during future app startup or a manual reload), it validates the corpus, instantiates all models, and exposes them for search and display. Failures are recorded in logs and surfaced through the validation report, while successfully parsed data remains available.
- **Invalid recipe visibility**: If a recipe file fails validation, the loader records a diagnostic summarizing the issues and excludes the recipe from the active catalog until fixed, enabling downstream layers to inform the user.

Acceptance criteria:

- Given a valid corpus, all recipes and ingredients load into memory within two seconds on target hardware.
- Given validation errors, the loader reports every issue discovered in that run and identifies the affected files.
- Given a recipe referencing an ingredient absent from the catalog, the loader represents it as an ad-hoc ingredient with name only, without raising a validation failure.
- Given ingredient catalog entries, the loader attaches optional translations and nutrition data to recipes that reference them.

## 4. Requirements

### Functional

- Define Python models:
  - `Recipe`: name, portions, optional description, ordered `RecipeIngredient` list, optional mise en place steps, optional method steps, and metadata (e.g., source path, timestamps).
  - `RecipeIngredient`: resolved `Ingredient` instance for the primary ingredient, quantity amount (numeric value plus required unit drawn from a constrained enum), and optional substitutes collection.
  - `Ingredient`: name, optional category (read from catalog file header when present), optional translations (mapping language code→string), optional nutrition info (per-unit metrics for sugar, protein, saturated fat, unsaturated fat), and metadata (source path when sourced from catalog, unit basis).
- Guarantee recipe and ingredient names are unique and human-readable without imposing filename-safety constraints; reject duplicate names during validation.
- Parse the filesystem structure rooted at the configured corpus path with `recipes/` and `ingredients/` subdirectories.
- Treat YAML filenames as diagnostic metadata only; rely on the unique `name` fields and the recorded `source_path` for identification.
- Instantiate models by reading each YAML file, supporting multiple ingredients per ingredient file.
- When a recipe references an ingredient name that exists in the catalog, attach the enriched `Ingredient` instance; otherwise create an ephemeral `Ingredient` with name only.
- Maintain relationships: recipes expose their ingredients, ingredients track the recipes that reference them (reverse index).
- Provide a loader service that returns a cohesive data object (e.g., `CorpusSnapshot`) containing collections, lookup indices, and validation reports.

### Data Model Detail

#### Recipe

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Display name shown in UI; must be unique across the corpus. |
| `description` | `str` | No | Optional summary text for listings. |
| `portions` | `int` | Yes | Number of servings for scaling and nutrition displays. |
| `ingredients` | `tuple[RecipeIngredient, ...]` | Yes | Ordered as declared in YAML. |
| `mise_en_place` | `tuple[str, ...]` | No | Optional ordered prep steps; empty tuple when omitted. |
| `method` | `tuple[str, ...]` | No | Optional ordered cooking steps; empty tuple when omitted. |
| `source_path` | `Path` | Yes | Absolute path to recipe file for diagnostics. |
| `metadata` | `Mapping[str, Any]` | No | Reserved for future per-recipe extras (e.g., tags). |

#### RecipeIngredient

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `ingredient` | `Ingredient` | Yes | Always populated; loader creates ephemeral `Ingredient` when no catalog entry exists. |
| `quantity` | `float` | Yes | Numeric amount stored as a floating-point value. |
| `unit` | `QuantityUnit` | Yes | Enum covering supported units (`g`, `kg`, `ml`, `l`, `tbsp`, `tsp`, `piece`). |
| `substitutes` | `tuple[Ingredient, ...]` | No | Optional ordered substitutes, each resolved to catalog or ephemeral entries. |

#### Ingredient

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Display name; must be unique across the corpus. |
| `category` | `str` | No | Read from catalog file header; falls back to filename-derived grouping when absent. |
| `translations` | `dict[str, str]` | No | Language code keyed translations (`"pl": "łosoś"`). |
| `nutrition` | `NutritionProfile` | No | Per-unit macros with declared basis. |
| `source_path` | `Path` | No | Present for catalog-managed ingredients; absent for ad-hoc ones. |
| `recipes` | `tuple[str, ...]` | Yes | Names of recipes referencing this ingredient. |

#### NutritionProfile

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `unit` | `QuantityUnit` | Yes | Base unit for macro values (e.g., `g`). |
| `per_amount` | `float` | Yes | Amount associated with macro values (e.g., per 100g). |
| `sugars` | `float` | No | Sugar grams per `per_amount`; optional. |
| `protein` | `float` | No | Protein grams per `per_amount`; optional. |
| `saturated_fat` | `float` | No | Saturated fat grams; optional. |
| `unsaturated_fat` | `float` | No | Unsaturated fat grams; optional. |

#### CorpusSnapshot

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `recipes` | `Mapping[str, Recipe]` | Yes | Keyed by recipe name for fast lookup. |
| `ingredients` | `Mapping[str, Ingredient]` | Yes | All ingredients keyed by name, regardless of catalog origin. |
| `validation_report` | `ValidationReport` | Yes | Aggregated errors/warnings from last load. |
| `generated_at` | `datetime` | Yes | Timestamp of snapshot creation. |

### Non-Functional

- Validation runs must complete within two seconds for 500 recipes and 200 ingredient entries on Raspberry Pi-class hardware.
- Data models are immutable after instantiation to prevent accidental runtime drift; mutations require reloading from disk.
- Validation must collect all issues per run and never leave the system in a partially updated state—either the previous snapshot remains active or the new snapshot replaces it atomically.
- Errors and warnings are logged with structured context (file path, field, message) and exposed to the UI via an observable status component.

### Data & Schema Changes

- Keep recipes in one-file-per-recipe YAML documents and ingredient catalogs in one-file-per-category YAML documents.
- Ingredient catalog files begin with an explicit `category` field and then list ingredient entries; when the field is absent, fall back to deriving the category from the filename for backward compatibility.
- Rely on the data models to validate structure and values; no external YAML schema definitions are required.
- Provide migration guidance for legacy files (e.g., missing category headers or duplicate names) within the validation report.

## 5. Experience Notes

- Expose validation summaries in a structured report so future UI or tooling can surface issues (e.g., “3 recipes skipped due to validation errors” with detail references).
- Include the recipe or ingredient name together with its source path in every diagnostic entry to help maintainers locate issues quickly.
- Favor error messages that point to exact YAML keys and propose fixes (e.g., “ingredients[2].amount.unit must be one of g, kg, ml, l, tbsp, tsp”).

## 6. Technical Design

- **Architecture**: Introduce a `data` package (`src/onyo/data/`) with:
  - `models.py`: frozen `@dataclass` or `pydantic` models for Recipe, RecipeIngredient, Ingredient, CorpusSnapshot.
  - `naming.py`: utilities to enforce uniqueness rules and derive helpful slugs without mutating display names.
  - `loader.py`: orchestrates filesystem traversal, model instantiation, and report generation.
  - `errors.py`: domain exceptions (e.g., `ValidationError`, `NameCollisionError`).
- **Name strategy**: detect duplicates early, provide colliding source paths in the validation report, and preserve original display names.
- **Validation pipeline**:
  1. Walk `ingredients/`, parse YAML into dictionaries, instantiate models, and capture model-creation errors while recording the category from file headers or filename fallback.
  2. Walk `recipes/`, instantiate models, ensure ingredient names resolve to catalog entries or create ephemeral placeholders, and attach any instantiation errors to the report.
  3. If a recipe references and ingredient which has nutrition info, it needs to use the same unit as the recipe, otherwise the nutritions will be scrapped from the ingredient and error will be logged.
  4. Collect all model and relationship validation errors in a `ValidationReport` containing items (level, file, field, message).
  5. Build reverse indices: ingredient name → recipes referencing it, recipe name → file path.
  6. If fatal errors exist, retain prior `CorpusSnapshot` and surface report; otherwise replace active snapshot.
- **Integration points**:
  - Expose a `DataStore` or dependency-injected service that provides read-only access to the current snapshot for UI and search layers.
  - Emit events or signals when new snapshots are activated so observers can refresh state.
- **Concurrency**: guard reloads with a lock to prevent overlapping filesystem reads.
- **Extensibility**: design quantity units as an enum with explicit conversion metadata to support future normalization (e.g., grams ↔ kilograms).

## 7. Testing Strategy

- Unit tests for naming utilities covering duplicate detection, slug derivation (when needed), and Unicode normalization behavior.
- Model validation tests using fixture YAML files:
  - Valid recipe/ingredient fixtures.
  - Failing scenarios (missing name, invalid units, duplicate names) that assert all errors are reported.
- Loader integration tests that construct temporary corpus directories and confirm:
  - Successful snapshot creation with correct counts and relationships.
  - Ephemeral ingredient creation when catalog entries are absent.
  - Reverse indices accurately list referencing recipes.
  - Previous snapshot remains active when validation fails.
- Performance smoke test measuring validation time against a synthetic corpus (skipped in CI but documented for manual verification).
- Contract tests (or component tests) that assert the validation report exposes message counts and per-file details needed by future UI layers.
