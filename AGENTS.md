# Agent Playbook

## Mission Brief

- Deliver thoughtful, production-safe help.
- Preserve the user's intent, use the provided toolchain, and leave the tree in
  a healthy state every time.
- Keep context fresh: read requirements, infer missing details reasonably, and
  avoid redundant questions.
- Prefer asking over doing, always question if things can be implemented in a
  more elegant, pythonic, or modular way.
- Deliver end‑to‑end. Don’t stop until the request is satisfied or truly blocked.

## Default Workflow Checklist

1. Clarify the task and check repo context before you edit anything.
   Restate goals, surface assumptions, and note constraints.
2. Use `rg`, `ls`, or `git status` to gather the minimal context you need.
3. If the tooling or tech is not specified, ask and offer your best picks.
4. Outline a plan when the work is non-trivial (skip only for simple edits).
5. Make focused changes; prefer small, composable functions and clear comments.
6. Format and lint the code after every change to any python file.
7. Add new tests when the code changes.
8. Execute targeted tests whenever you change any python code or test data.
9. Summarize what changed, call out follow-ups, and reference touched paths.

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

Always run commands from the repo root. Any command which rely on the virtual
environment needs to be called with `uv run` prefix.
Always keep the repository formatted and linted and all the tests passing.

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
- Make use of pytest fixtures and organized common fixtures into `conftest.py`
  modules.
- Make use of test parametrization.
- Structure tests Arrange → Act → Assert and cover edge cases and regressions.
- Keep coverage high on any code you touch; add new tests when behavior shifts,
  unles instructed otherwise.

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
- Commit messages: `<type>(<scope>): <description>`.
  - If the change closed a numbered task, reference the task in the description.
  - Types are `feat`, `fix`, `test`, `refactor`, `docs`, `chore`.
  - Example: `feat(cli): implement cli, close task 3.14`.
- Document residual risks or required manual checks in your summary.
