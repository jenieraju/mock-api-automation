# AGENTS.md

Always-on conventions for coding agents working in this repository. Keep this file short.

App / API under test: public **JSONPlaceholder** mock REST API (`API_BASE_URL`). Humans and agents should also read [README.md](README.md) for structure and [CONTRIBUTING.md](CONTRIBUTING.md) for PR workflow.

## Scope

- Automate the **Users** and **Posts** subset only unless the task expands scope.
- Do not add UI/browser tests here.
- Do not commit secrets, `.env` files with real credentials, or generated report folders.

## Architecture

```
tests/  →  conftest fixtures + utils/assertions  →  HTTP (requests)  →  mock API
```

| Layer | Path | Responsibility |
|-------|------|----------------|
| Tests | `tests/test_*.py` | Scenarios, markers, asserts |
| Fixtures | `conftest.py` | `api_client`, `base_url`, `timeout`, `settings` |
| Config | `config/settings.py` | Env loading via `get_settings()` |
| Helpers | `utils/assertions.py` | Shared response checks |

Never hardcode the base URL in tests — use the `base_url` fixture.

## Test style (mandatory)

- Markers: `@pytest.mark.positive` | `negative` | `edge`
- Naming: `test_<snake_case>`
- Body sections: `# Arrange` / `# Act` / `# Assert`
- Docstring: short scenario description (include resource + intent)
- Imports: keep minimal; reuse `assert_status` / `assert_json_keys` when useful

## Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
pytest -m positive
pytest tests/test_users.py -v
```

## Before finishing a task

1. `pytest` exits 0.
2. Docs updated if structure, commands, or covered endpoints changed.
3. Open a PR from a feature branch (see CONTRIBUTING.md) — do not push straight to `main` for feature work when a PR is required.
