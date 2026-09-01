# Mock API Automation

Pytest automation for the ReqRes API (`swagger.yaml`, OpenAPI 3.0.3), covering
the create and delete user flows.

## Layout

| File | Purpose |
| --- | --- |
| `conftest.py` | Config options, `ApiClient` wrapper, auth + user fixtures |
| `tests/test_users.py` | `POST /users` and `DELETE /users/{id}` coverage |
| `pytest.ini` | Test paths and markers (`smoke`, `users`) |
| `.env` | API key and base URL (gitignored; see `.env.example`) |

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # then add your x-api-key
```

## Run

```bash
.venv/bin/pytest                      # whole suite
.venv/bin/pytest -m smoke             # happy paths only
.venv/bin/pytest --api-key=<key>      # override the key ad hoc
.venv/bin/pytest --base-url=http://localhost:3000/api
```

Settings resolve in this order: CLI flag → environment variable → `.env` →
built-in default. The API key has no default; supply it one of those ways.

## Fixtures

- `api` — session-scoped authenticated client (`x-api-key` header preset).
- `user_payload` — a unique `CreateUserRequest` body per test (UUID-suffixed
  email), so reruns never collide.
- `created_user` — creates a user, yields the response body, and deletes it on
  teardown. Cleanup failures print a warning instead of failing the test.

## Known spec gap

`test_write_without_api_key_is_rejected` is marked `xfail`: the spec declares a
global `ApiKeyAuth` requirement, but the live demo endpoints accept
unauthenticated writes (`201`/`204` with a `legacy_success` marker). It will
xpass if enforcement is ever enabled.
