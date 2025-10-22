# Feature PRD: Data Model

## 1. Feature Overview

The Data Model feature establishes the in-memory representation of the recipe corpus and the validation logic that keeps it trustworthy. It introduces typed models for recipes, their ingredient usage, and the shared ingredient catalog, providing a single source of truth for the rest of the application. The feature ensures the clear-text YAML repository can be loaded into Python objects with rigorous schema checks and actionable feedback when data issues arise.

This work resolves the current gap between the external YAML corpus and the application runtime. Once complete, the NiceGUI UI, search layer, and future services will read from well-defined models that accurately mirror the corpus structure and relationships.

## 2. Goals & Non-Goals

- Deliver immutable Python domain classes for `Recipe`, `RecipeIngredient`, and `Ingredient`, enforcing filename-safe naming rules.
- Load the corpus from disk into those classes on application startup and manual refresh.
- Validate recipe and ingredient YAML against hardcoded schemas, accumulating all errors per run.
- Surface validation outcomes so users understand when data failed to load and why.
- Prepare the models for downstream consumers (search, UI) without locking in those implementations.

Non-goals:

- Building search, filtering, or presentation logic (they will consume the models once available).
- Allowing write-back or mutation of the YAML corpus from the app.
- Introducing a persistence layer beyond the existing clear-text repository.

## 3. User Impact & Flows

- **Corpus load on startup/refresh**: When the app boots or a manual reload is triggered, it validates the corpus, instantiates all models, and exposes them for search and display. Failures are reported in logs and through a user-facing alert banner, while successfully parsed data remains available.
- **Invalid recipe visibility**: If a recipe file fails validation, the user sees a notification summarizing the issues and the recipe is excluded from the active catalog until fixed.

Acceptance criteria:

- Given a valid corpus, all recipes and ingredients load into memory within two seconds on target hardware.
- Given schema violations, the loader reports every issue discovered in that run and identifies the affected files.
- Given a recipe referencing an ingredient absent from the catalog, the loader represents it as an ad-hoc ingredient with name only, without raising a validation failure.
- Given ingredient catalog entries, the loader attaches optional translations and nutrition data to recipes that reference them.

## 4. Requirements

### Functional

- Define Python models:
  - `Recipe`: name, portions, optional description, ordered `RecipeIngredient` list, optional mise en place steps, optional method steps, and metadata (e.g., source path, timestamps).
  - `RecipeIngredient`: resolved `Ingredient` instance for the primary ingredient, quantity amount (numeric value plus required unit drawn from a constrained enum), and optional substitutes collection.
  - `Ingredient`: name, optional category (folder-derived when present), optional translations (mapping language code→string), optional nutrition info (per-unit metrics for sugar, protein, saturated fat, unsaturated fat), and metadata (source path when sourced from catalog, unit basis).
- Guarantee recipe and ingredient names are unique, human-readable, and remain valid YAML filenames; reject conflicts or unsafe names during validation.
- Parse the filesystem structure rooted at the configured corpus path with `recipes/` and `ingredients/` subdirectories.
- Instantiate models by reading each YAML file, supporting multiple ingredients per ingredient file.
- When a recipe references an ingredient name that exists in the catalog, attach the enriched `Ingredient` instance; otherwise create an ephemeral `Ingredient` with name only.
- Maintain relationships: recipes expose their ingredients, ingredients track the recipes that reference them (reverse index).
- Provide a loader service that returns a cohesive data object (e.g., `CorpusSnapshot`) containing collections, lookup indices, and validation reports.

### Data Model Detail

#### Recipe

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Display name shown in UI; must also be a filesystem-safe filename. |
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
| `quantity` | `Decimal` | Yes | Numeric amount stored as high-precision decimal. |
| `unit` | `QuantityUnit` | Yes | Enum covering supported units (`g`, `kg`, `ml`, `l`, `tbsp`, `tsp`, `cup`, `piece`). |
| `substitutes` | `tuple[Ingredient, ...]` | No | Optional ordered substitutes, each resolved to catalog or ephemeral entries. |

#### Ingredient

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Display name; must be usable as a YAML filename. |
| `category` | `str` | No | Derived from catalog file grouping when present. |
| `translations` | `dict[str, str]` | No | Language code keyed translations (`"pl": "łosoś"`). |
| `nutrition` | `NutritionProfile` | No | Per-unit macros with declared basis. |
| `source_path` | `Path` | No | Present for catalog-managed ingredients; absent for ad-hoc ones. |
| `recipes` | `tuple[str, ...]` | Yes | Names of recipes referencing this ingredient. |

#### NutritionProfile

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `unit` | `QuantityUnit` | Yes | Base unit for macro values (e.g., `g`). |
| `per_amount` | `Decimal` | Yes | Amount associated with macro values (e.g., per 100g). |
| `sugars` | `Decimal` | No | Sugar grams per `per_amount`; optional. |
| `protein` | `Decimal` | No | Protein grams per `per_amount`; optional. |
| `saturated_fat` | `Decimal` | No | Saturated fat grams; optional. |
| `unsaturated_fat` | `Decimal` | No | Unsaturated fat grams; optional. |

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

- Author YAML schemas (using Yamale or PyYAML-based validation) for:
  - Recipe files: enforce required `name` matching the YAML filename, required numeric `portions`, `ingredients` array with amount + unit + ingredient name, optional `mise_en_place` step list, optional `method` step list.
  - Ingredient files: enforce per-file list structure with `name`, optional `category`, optional `translations` map, optional `nutrition` block with numeric macros and declared unit basis.
- Schemas live in code and version alongside the loader; updates require explicit migration notes.
- Store the ingredient category derived from the source file path (e.g., `ingredients/Fish and Meat.yaml` → `"Fish and Meat"`).
- Provide migration guidance for legacy files (e.g., filenames not matching `name`) within the validation report.

## 5. Experience Notes

- In the web UI, display a persistent, dismissible banner summarizing validation problems (e.g., “3 recipes skipped due to schema errors — view details”). Link to a modal or log location that lists each issue.
- When showing diagnostics, reference the recipe or ingredient name along with its filename to help users locate issues quickly.
- Favor error messages that point to exact YAML keys and propose fixes (e.g., “ingredients[2].amount.unit must be one of g, kg, ml, l, tbsp, tsp”).

## 6. Technical Design

- **Architecture**: Introduce a `data` package (`src/onyo/data/`) with:
  - `models.py`: frozen `@dataclass` or `pydantic` models for Recipe, RecipeIngredient, Ingredient, CorpusSnapshot.
  - `naming.py`: utilities to validate and sanitize names for filesystem use without altering their display form.
  - `schemas/`: YAML schema definitions loaded at runtime for validation.
  - `loader.py`: orchestrates filesystem traversal, schema validation, model instantiation, and report generation.
  - `errors.py`: domain exceptions (e.g., `SchemaValidationError`, `NameCollisionError`).
- **Name safety strategy**: ensure every recipe and ingredient name converts to a safe filename, detect conflicts early, and store the original name for display.
- **Validation pipeline**:
  1. Walk `ingredients/`, validate each file against the ingredient schema, and build ingredient objects with category from folder/file metadata.
  2. Walk `recipes/`, validate against recipe schema, ensure ingredient names resolve to catalog entries or create ephemeral placeholders, and instantiate recipes.
  3. Collect all validation errors in a `ValidationReport` containing items (level, file, field, message).
  4. Build reverse indices: ingredient name → recipes referencing it, recipe name → file path.
  5. If fatal errors exist, retain prior `CorpusSnapshot` and surface report; otherwise replace active snapshot.
- **Integration points**:
  - Expose a `DataStore` or dependency-injected service that provides read-only access to the current snapshot for UI and search layers.
  - Emit events or signals when new snapshots are activated so observers can refresh state.
- **Concurrency**: guard reloads with a lock to prevent overlapping filesystem reads.
- **Extensibility**: design quantity units as an enum with explicit conversion metadata to support future normalization (e.g., grams ↔ kilograms).

## 7. Testing Strategy

- Unit tests for naming utilities covering filename-safety checks, collisions, and Unicode fold-down behavior.
- Schema validation tests using fixture YAML files:
  - Valid recipe/ingredient fixtures.
  - Failing scenarios (missing name, invalid units, name/filename mismatches) that assert all errors are reported.
- Loader integration tests that construct temporary corpus directories and confirm:
  - Successful snapshot creation with correct counts and relationships.
  - Ephemeral ingredient creation when catalog entries are absent.
  - Reverse indices accurately list referencing recipes.
  - Previous snapshot remains active when validation fails.
- Performance smoke test measuring validation time against a synthetic corpus (skipped in CI but documented for manual verification).
- UI-facing tests (or component tests) asserting that validation banners appear when the loader exposes errors.
