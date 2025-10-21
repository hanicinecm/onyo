# Agent Playbook

## Mission Brief

- Provide thoughtful, production-safe help.
- Preserve the user's intent, stay within the provided toolchain, and leave the
  tree in a healthy state every time.
- Keep context fresh: read requirements, infer missing details reasonably, and
  avoid redundant questions.
- Ask before doing when unsure, and challenge whether solutions can be more
  elegant, pythonic, or modular.
- Deliver end-to-end and pause only when the request is satisfied or truly
  blocked.

## Default Workflow Checklist

1. Clarify the task and check repo context before editing.
   Restate goals, surface assumptions, and note constraints.
2. Use `rg`, `ls`, or `git status` to gather the minimal context you need.
3. If the tooling or tech is unspecified, ask and propose the best options.
4. Outline a plan when the work is non-trivial (skip only for simple edits).
5. Make focused changes; prefer small, composable functions and clear comments.
6. Format and lint the code after every change to any python file with
   `uvx ruff check --fix && uvx ruff format`.
7. Add new tests, when applicable, and run them.
8. Summarize what changed, call out follow-ups, and reference touched paths.

## Project Layout

- Source code lives under `src/onyo/`; structure logically into modules or
  sub-packages, as needed.
- Tests live in `tests/` and mirror the source tree
  (e.g., `src/onyo/foo.py` → `tests/test_foo.py`).
- Quick and dirty development scripts and manual testing code lives in `sandbox/`
  and is always kept git-ignored.
- Top-level configs: `pyproject.toml`, `.gitignore`, `AGENTS.md`, etc.
  The `pyproject.toml` is compatible with `uv`.

## Toolbelt

- Format: `uvx ruff format .`
- Lint: `uvx ruff check .` (append `--fix` for safe autofixes)
- Tests: `uv run pytest` or target cases like
  `uv run pytest tests/onyo/test_foo.py::test_bar`
- Dependencies: `uv add <pkg>`; dev-only deps use `uv add --dev <pkg>`

Always run commands from the repo root. Any command that relies on the virtual
environment needs the `uv run` prefix.
Keep the repository formatted, linted, and with all tests passing.

## Coding Style and Standards

- Indent with 4 spaces.
- Add type hints everywhere and keep both the public and private surface typed.
- Write Google-style docstrings (no types inside docstrings; rely on hints).
  Document exceptions.
- Do not forget docstrings on top of the modules.
- Cap lines at 88 characters (black/ruff default).
- Favor short, composable functions over deep inheritance.
- Prioritize readability over cleverness.
- Use succinct comments to clarify non-obvious intent; avoid narrating the
  obvious.
- Always prefer `pathlib` over `os`.
- Avoid relative imports.
- Format and lint with `uvx ruff`.

## Testing Discipline

- Use `pytest` with files named `tests/**/test_*.py`.
- Always prefer test functions over test classes.
- Prefer pytest fixtures and organize shared fixtures in `conftest.py` modules.
- Parametrize tests where it improves coverage.
- Structure tests Arrange → Act → Assert and cover edge cases and regressions.
- Keep coverage high on code you touch; add tests when behavior shifts, unless
  instructed otherwise.

### Examples

```python
# file: conftest.py

@pytest.fixture
def resources_dir() -> Path:
    return Path(__file__).parent / "resources"

```

## Git & Collaboration

- Never discard user changes; if conflicts arise, ask before rewriting.
- Never commit unless asked for.
- Use the conventional commit format: `<type>(<scope>): <description>`.
  - If the change closed a numbered task, reference the task in the description.
  - Types are `feat`, `fix`, `test`, `refactor`, `docs`, `chore`.
  - Example: `feat(cli): implement cli, close task 3.14`.
- Branches:
  - The `main` branch (or `master`) should never be touched by agents.
  - The development happens on the `dev` branch, and/or on feature branches.
- Document residual risks or required manual checks in your summary.
