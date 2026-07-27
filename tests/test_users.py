"""Users resource tests against JSONPlaceholder mock API."""

from __future__ import annotations

import pytest

from utils.assertions import assert_json_keys, assert_status


@pytest.mark.positive
def test_list_users_returns_collection(api_client, base_url, timeout):
    """MOCK-API — GET /users returns a non-empty list of users."""
    # Arrange
    url = f"{base_url}/users"

    # Act
    response = api_client.get(url, timeout=timeout)

    # Assert
    assert_status(response, 200)
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1
    assert_json_keys(users[0], ("id", "name", "username", "email"))


@pytest.mark.positive
def test_get_user_by_id_returns_expected_fields(api_client, base_url, timeout):
    """MOCK-API — GET /users/1 returns a single user with core fields."""
    # Arrange
    user_id = 1
    url = f"{base_url}/users/{user_id}"

    # Act
    response = api_client.get(url, timeout=timeout)

    # Assert
    assert_status(response, 200)
    user = response.json()
    assert user["id"] == user_id
    assert_json_keys(user, ("id", "name", "username", "email", "address", "company"))
    assert isinstance(user["email"], str) and "@" in user["email"]


@pytest.mark.negative
def test_get_user_not_found_returns_404(api_client, base_url, timeout):
    """MOCK-API — GET /users/{missing} returns 404 for an unknown id."""
    # Arrange
    url = f"{base_url}/users/99999"

    # Act
    response = api_client.get(url, timeout=timeout)

    # Assert
    assert_status(response, 404)


@pytest.mark.edge
def test_create_user_returns_created_resource(api_client, base_url, timeout):
    """MOCK-API — POST /users echoes payload and assigns an id (mock create)."""
    # Arrange
    url = f"{base_url}/users"
    payload = {"name": "QA Agent", "username": "qa_agent", "email": "qa.agent@example.com"}

    # Act
    response = api_client.post(url, json=payload, timeout=timeout)

    # Assert
    assert response.status_code in (200, 201), (
        f"Expected 200/201, got {response.status_code}: {response.text[:500]}"
    )
    body = response.json()
    assert body["name"] == payload["name"]
    assert body["username"] == payload["username"]
    assert body["email"] == payload["email"]
    assert "id" in body
