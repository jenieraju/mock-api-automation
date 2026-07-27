# Mock API Automation

Pytest-based REST API automation for a **subset** of the [JSONPlaceholder](https://jsonplaceholder.typicode.com/) public mock APIs.

This repository is designed so that both humans and coding agents can understand the layout, run tests, and extend coverage safely.

## What is automated

| Resource | Methods covered | Notes |
|----------|-----------------|-------|
| **Users** | `GET /users`, `GET /users/{id}`, `POST /users` | List, fetch, create (mock), 404 |
| **Posts** | `GET /posts`, `GET /posts/{id}`, `POST /posts`, `PUT /posts/{id}`, `DELETE /posts/{id}`, filtered `GET /posts?userId=` | CRUD subset + query filter + 404 |

JSONPlaceholder simulates writes (create/update/delete) without persisting data. Assertions focus on status codes and response shape.

Out of scope for this subset: Comments, Albums, Photos, Todos.

## Project structure

```
mock-api-automation/
├── AGENTS.md              # Short agent-oriented conventions (read first)
├── CONTRIBUTING.md        # How to add tests and open PRs
├── README.md              # This file
├── .env.example           # Environment variable template
├── conftest.py            # Shared fixtures (api_client, base_url, timeout)
├── pytest.ini             # Markers and default pytest options
├── requirements.txt       # Python dependencies
├── config/
│   └── settings.py        # Env-driven settings (API_BASE_URL, API_TIMEOUT)
├── utils/
│   └── assertions.py      # Shared status/JSON helpers
└── tests/
    ├── test_users.py      # Users resource scenarios
    └── test_posts.py      # Posts resource scenarios
```

## Test framework

| Item | Choice |
|------|--------|
| Language | Python 3.10+ |
| Runner | **pytest** |
| HTTP client | **requests** (session fixture `api_client`) |
| Config | `python-dotenv` + `config/settings.py` |
| Markers | `@pytest.mark.positive` / `negative` / `edge` |

### Conventions (must follow)

- One test function per scenario; name as `test_<snake_case_scenario>`.
- Structure body with `# Arrange` / `# Act` / `# Assert` comments.
- Use fixtures from `conftest.py` — do **not** redefine `api_client`, `base_url`, or `timeout`.
- Build URLs as `f"{base_url}{endpoint}"`.
- Keep secrets and hostnames out of test modules; use `get_settings()` / env vars.
- Prefer helpers in `utils/assertions.py` for status and key checks.

## Prerequisites

- Python 3.10 or newer
- Network access to `https://jsonplaceholder.typicode.com` (or your override base URL)

## Setup

```bash
git clone https://github.com/jenieraju/mock-api-automation.git
cd mock-api-automation
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional; defaults already target JSONPlaceholder
```

## Execution

```bash
# Full suite
pytest

# By marker
pytest -m positive
pytest -m negative
pytest -m edge

# Single module / test
pytest tests/test_users.py -v
pytest tests/test_posts.py::test_create_post_returns_created_resource -v
```

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `https://jsonplaceholder.typicode.com` | Mock API base URL (no trailing slash required) |
| `API_TIMEOUT` | `30` | Per-request timeout in seconds |

## Agent quick start

If you are an AI coding agent working in this repo:

1. Read [AGENTS.md](AGENTS.md) for always-on rules.
2. Run `pytest` after any test change; do not open a PR until the suite is green.
3. Follow [CONTRIBUTING.md](CONTRIBUTING.md) for branch/PR expectations.
4. Extend only documented resources unless the task explicitly expands scope.

## License

MIT — for learning and internal QA automation demos.
