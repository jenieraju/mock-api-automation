"""Shared pytest configuration and fixtures for the ReqRes API suite.

Contract under test: /home/issac/Downloads/swagger/swagger.yaml (ReqRes API 1.0.0).
Auth is an API key sent in the `x-api-key` header (securitySchemes.ApiKeyAuth).
"""

import os
import pathlib
import time
import uuid

import pytest
import requests

DEFAULT_BASE_URL = "https://reqres.in/api"
DEFAULT_TIMEOUT = 15
ENV_FILE = pathlib.Path(__file__).parent / ".env"


def _from_env_file(name):
    """Read one KEY=value out of a gitignored .env, without extra dependencies."""
    if not ENV_FILE.is_file():
        return None
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == name:
            return value.strip().strip('"').strip("'")
    return None


def _setting(name, fallback=None):
    """Precedence: real environment variable, then .env, then the fallback."""
    return os.getenv(name) or _from_env_file(name) or fallback


def pytest_addoption(parser):
    """Expose the environment knobs as CLI flags so CI can override them."""
    parser.addoption(
        "--base-url",
        action="store",
        default=_setting("REQRES_BASE_URL", DEFAULT_BASE_URL),
        help="Base URL of the ReqRes API (servers[0].url in the spec).",
    )
    parser.addoption(
        "--api-key",
        action="store",
        default=_setting("REQRES_API_KEY"),
        help="Value for the x-api-key header.",
    )
    parser.addoption(
        "--timeout",
        action="store",
        type=float,
        default=float(_setting("REQRES_TIMEOUT", DEFAULT_TIMEOUT)),
        help="Per-request timeout in seconds.",
    )


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return pytestconfig.getoption("--base-url").rstrip("/")


@pytest.fixture(scope="session")
def api_key(pytestconfig):
    key = pytestconfig.getoption("--api-key")
    if not key:
        pytest.fail("No API key supplied: pass --api-key or set REQRES_API_KEY.")
    return key


@pytest.fixture(scope="session")
def timeout(pytestconfig):
    return pytestconfig.getoption("--timeout")


class ApiClient:
    """Thin requests wrapper: joins paths onto the base URL and keeps auth headers.

    Every call returns the raw `requests.Response` so tests own the assertions.
    """

    def __init__(self, base_url, api_key, timeout):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "x-api-key": api_key,
                "Accept": "application/json",
            }
        )

    def request(self, method, path, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        url = f"{self.base_url}/{path.lstrip('/')}"
        return self.session.request(method, url, **kwargs)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

    def close(self):
        self.session.close()


@pytest.fixture(scope="session")
def api(base_url, api_key, timeout):
    """Authenticated client shared by the whole session."""
    client = ApiClient(base_url, api_key, timeout)
    yield client
    client.close()


@pytest.fixture
def user_payload():
    """A unique CreateUserRequest body, so reruns never collide on email."""
    suffix = uuid.uuid4().hex[:8]
    return {
        "email": f"isaac.test.{suffix}@reqres.in",
        "first_name": "isaac",
        "last_name": f"test-{suffix}",
    }


@pytest.fixture
def created_user(api, user_payload):
    """Create a user for tests that need one, and delete it on teardown.

    Yields the parsed CreateUserResponse body. Teardown is best-effort: the
    delete is retried nowhere and failures are surfaced as a warning, not an
    error, so cleanup can never mask a test result.
    """
    response = api.post("/users", json=user_payload)
    assert response.status_code == 201, (
        f"Setup failed to create user: {response.status_code} {response.text}"
    )
    user = response.json()

    yield user

    cleanup = api.delete(f"/users/{user['id']}")
    if cleanup.status_code not in (204, 404):
        print(
            f"\n[cleanup] DELETE /users/{user['id']} returned "
            f"{cleanup.status_code}: {cleanup.text}"
        )


@pytest.fixture(autouse=True)
def _pace_requests():
    """ReqRes rate-limits bursts from a single key; space calls out slightly."""
    yield
    time.sleep(0.3)
