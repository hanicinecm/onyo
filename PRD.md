# Project PRD: onyo

## 1. Project Overview

onyo is a personal recipe manager that keeps a curated library of clear-text recipes and serves them through a clean, clutter-free interface. It solves the common problem of scattered, inconsistent recipe notes by giving the household an authoritative, easily tweakable source of truth that works across desktop and mobile browsers on the home network.

## 2. Context, Constraints & Assumptions

- The recipe corpus lives in a separate, git-controlled repository of YAML files maintained exclusively by the household. The onyo application reads from this repository in read-only fashion.
- A Raspberry Pi (or similar low-power device) will host the application on the local network. Only two concurrent users (the couple) are expected, and no authentication or remote access is required.
- All data remains offline; there is no integration with third-party APIs or cloud services. Nutritional and translation details must come from manually curated ingredient metadata.
- The NiceGUI framework is the preferred UI layer, and the repo already targets Python 3.13 managed via `uv`.
- The application must enforce a documented YAML schema for recipes and ingredient catalogs, failing gracefully on invalid data.

## 3. Objectives & Scope

- Deliver a self-hosted app that surfaces the curated recipe collection with fast ingredient-based search and modular filtering.
- Provide a distraction-free reading experience optimized for simultaneous use on desktop and mobile browsers.
- Ensure the app can validate, read, and refresh recipe data from an external filesystem path with minimal configuration.

In scope for the initial release:

- Schema definition and validation for recipe and ingredient YAML files.
- Local configuration that points the app at the external recipe repository.
- Search experience centered on ingredient lookups with room for additional filters.
- Responsive web UI (NiceGUI) for browsing, reading, and tweaking recipes during cooking.
- Foundations for nutritional display drawn from ingredient metadata when available.

Out of scope / future work:

- Generating PDFs of recipes, shopping lists, or freezer labels.
- Automated shopping list generation and export.
- Cooking history tracking, personalized recommendations, or random suggestions.
- Multi-user authentication, permissions, or remote access paradigms.

## 4. User Personas & Scenarios

### Personas

- **Martin – Curious Home Cook**: Maintains the recipe corpus, experiments frequently, wants fast ingredient lookups and confidence that edits are preserved cleanly. Pain point: scattered handwritten notes and unreliable web recipes. Values the ease of adjusting the recipes dynamically directly in the source, based on experimentation.
- **Alicja – Pragmatic Sous Chef**: Uses the app on a tablet or phone while helping in the kitchen, values clear step-by-step guidance and nutritional insight. Pain point: bloated recipe websites and difficulty tracking consistent instructions.

### Key Scenarios

- **Find by Ingredient**: User searches for “shallot” to discover all recipes using that ingredient, then opens one to review steps.
- **Browse Recipe Catalog**: User pulls up the full recipe list, optionally sorted or grouped, to scan what is available before deciding what to cook.
- **Find by Name**: User types part of a recipe title (e.g., “borscht”) to open the exact recipe without scanning the full catalog.
- **Kitchen Companion View**: User opens a recipe on a mobile device, scans the mise en place, and follows the step list without scrolling through unrelated content.
- **Inline Tweaks & Refresh**: Martin edits YAML files in the repo (e.g., adding nutritional data) and expects the app to detect updates quickly (manual refresh acceptable).

## 5. Experience & Capabilities

- **Interface**: A NiceGUI-powered web application served on the LAN. Layout adapts to both phone and widescreen browsers, prioritizing readable typography, collapsible sections for mise en place and steps, and minimal decorative content.
- **Search & Filtering**: Ingredient-keyword search as the primary entry point, with extensible filter hooks (e.g., cuisine, difficulty, prep time) designed for future expansion. Results should show key metadata (prep time, portion size) at a glance.
- **Recipe Detail View**: Displays title, short description, ingredient list with measurements, mise en place notes, and sequential steps. Nutritional data appears when present for each ingredient or aggregated per portion.
- **Data Handling**: The app loads recipes and ingredient metadata from a configured filesystem path, validates files against schema, and surfaces helpful errors for malformed entries. Users trigger a manual “reload recipes” action to pick up changes made in the repository.
- **Accessibility & Reliability**: Pages load quickly on local network with small asset footprint. Text contrast and scaling support comfortable cooking scenarios. App remains functional offline once the Pi is powered.

## 6. Technical Strategy

- **Platform & Tooling**: Python 3.13 with dependency management via `uv`. NiceGUI for UI components, FastAPI (via NiceGUI) for routing, Yamale for YAML schema validation, and Pydantic for internal data models where helpful.
- **Data Model**: YAML-based storage. Each recipe lives in its own file; ingredient catalog organized per category. Define and document schemas (e.g., via JSON Schema or Pydantic models) to validate structure and enforce required fields.
- **Integration with Recipe Repo**: Configuration file or environment variable specifies the path to the recipe repository. Access uses `pathlib`, and validation runs on startup and on-demand reload. The app treats the repo as read-only.
- **Modular Architecture**: Separate modules for data loading/parsing, validation, search indexing, and presentation. Keep business logic independent from the UI framework to ease testing and future interface experiments.
- **Testing & Quality**: Unit tests for parsers, schema validators, and search utilities; integration tests for end-to-end recipe loading. Continuous formatting/linting enforced via `uvx ruff check --fix` and `uvx ruff format`.
- **Deployment**: Systemd service or simple script to run the NiceGUI server on Raspberry Pi, binding to LAN-accessible port. No containerization required initially, but design should permit future packaging if needed.

## 7. Risks, Open Questions & Next Steps

- **Schema Complexity** (Medium likelihood, Medium impact): Designing a flexible yet enforceable YAML schema that handles optional nutritional data without overcomplication. Mitigation: iterate with sample recipes, enforce validation with clear error messaging.
- **Performance of YAML Parsing on Pi** (Low likelihood, Medium impact): Large collections could slow startup or reloads. Mitigation: cache parsed representations and re-parse only changed files.
- **NiceGUI on Raspberry Pi** (Low likelihood, Low impact): Resource constraints might affect responsiveness. Mitigation: prototype early and monitor memory/CPU usage; fall back to a leaner UI stack if necessary.
- **Mobile Usability** (Medium likelihood, Medium impact): Ensuring large tap targets and stable layout during cooking. Mitigation: incorporate responsive design testing and gather real-world feedback in the kitchen.

Open questions:

- Preferred mechanism for adding/editing recipes from the app (if ever) vs relying purely on external editors.
- Formatting guidelines for future export features (PDF layout, freezer labels) when they enter scope.
