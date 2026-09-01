"""Create and delete coverage for the ReqRes /users endpoints.

Spec references:
  POST   /users      -> 201, CreateUserResponse
  DELETE /users/{id} -> 204, no content
"""

from datetime import datetime, timezone

import pytest
import requests

pytestmark = pytest.mark.users


def _parse_created_at(value):
    """CreateUserResponse.createdAt is RFC 3339 with a `Z` suffix."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


# --------------------------------------------------------------------------
# POST /users
# --------------------------------------------------------------------------


@pytest.mark.smoke
def test_create_user_returns_201(api, user_payload):
    response = api.post("/users", json=user_payload)

    assert response.status_code == 201, response.text
    assert "application/json" in response.headers.get("Content-Type", "")

    body = response.json()
    for field in ("email", "first_name", "last_name"):
        assert body[field] == user_payload[field], f"{field} was not echoed back"

    api.delete(f"/users/{body['id']}")


def test_create_user_response_matches_spec_schema(created_user):
    """id is a string and createdAt is a UTC timestamp at roughly 'now'."""
    assert set(created_user) >= {
        "email",
        "first_name",
        "last_name",
        "id",
        "createdAt",
    }

    assert isinstance(created_user["id"], str) and created_user["id"]

    created_at = _parse_created_at(created_user["createdAt"])
    age_seconds = (datetime.now(timezone.utc) - created_at).total_seconds()
    assert -60 < age_seconds < 300, f"createdAt looks wrong: {created_at}"


# --------------------------------------------------------------------------
# DELETE /users/{id}
# --------------------------------------------------------------------------


@pytest.mark.smoke
def test_delete_user_returns_204_and_empty_body(api, user_payload):
    created = api.post("/users", json=user_payload)
    assert created.status_code == 201, created.text
    user_id = created.json()["id"]

    response = api.delete(f"/users/{user_id}")

    assert response.status_code == 204, response.text
    assert response.text == "", "204 responses must carry no content"


# --------------------------------------------------------------------------
# Authentication (spec vs. live behaviour)
# --------------------------------------------------------------------------


@pytest.mark.xfail(
    reason=(
        "Spec declares a global ApiKeyAuth requirement, but the live ReqRes demo "
        "endpoints answer unauthenticated writes with 201/204 and a "
        "'legacy_success' marker. Kept as a known spec/implementation gap: this "
        "will xpass if key enforcement is ever turned on."
    ),
    strict=False,
)
@pytest.mark.parametrize(
    "method,path",
    [
        pytest.param("POST", "/users", id="create"),
        pytest.param("DELETE", "/users/2", id="delete"),
    ],
)
def test_write_without_api_key_is_rejected(base_url, timeout, method, path):
    kwargs = {"timeout": timeout}
    if method == "POST":
        kwargs["json"] = {
            "email": "no.key@reqres.in",
            "first_name": "no",
            "last_name": "key",
        }

    response = requests.request(method, f"{base_url}{path}", **kwargs)

    assert response.status_code == 401, (
        f"Expected 401 without x-api-key, got {response.status_code}: {response.text}"
    )


# --------------------------------------------------------------------------
# End-to-end
# --------------------------------------------------------------------------


@pytest.mark.smoke
def test_create_then_delete_user_lifecycle(api, user_payload):
    create = api.post("/users", json=user_payload)
    assert create.status_code == 201, create.text
    user_id = create.json()["id"]

    delete = api.delete(f"/users/{user_id}")
    assert delete.status_code == 204, delete.text
