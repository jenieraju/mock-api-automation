"""Posts resource tests against JSONPlaceholder mock API."""

from __future__ import annotations

import pytest

from utils.assertions import assert_json_keys, assert_status


@pytest.mark.positive
def test_list_posts_returns_collection(api_client, base_url, timeout):
    """MOCK-API — GET /posts returns a non-empty list of posts."""
    # Arrange
    url = f"{base_url}/posts"

    # Act
    response = api_client.get(url, timeout=timeout)

    # Assert
    assert_status(response, 200)
    posts = response.json()
    assert isinstance(posts, list)
    assert len(posts) >= 1
    assert_json_keys(posts[0], ("userId", "id", "title", "body"))


@pytest.mark.positive
def test_get_post_by_id_returns_expected_fields(api_client, base_url, timeout):
    """MOCK-API — GET /posts/1 returns a single post with core fields."""
    # Arrange
    post_id = 1
    url = f"{base_url}/posts/{post_id}"

    # Act
    response = api_client.get(url, timeout=timeout)

    # Assert
    assert_status(response, 200)
    post = response.json()
    assert post["id"] == post_id
    assert_json_keys(post, ("userId", "id", "title", "body"))
    assert isinstance(post["title"], str) and len(post["title"]) > 0


@pytest.mark.positive
def test_create_post_returns_created_resource(api_client, base_url, timeout):
    """MOCK-API — POST /posts creates a mock post and returns an id."""
    # Arrange
    url = f"{base_url}/posts"
    payload = {"title": "Automation smoke", "body": "Created by mock-api-automation", "userId": 1}

    # Act
    response = api_client.post(url, json=payload, timeout=timeout)

    # Assert
    assert_status(response, 201)
    body = response.json()
    assert body["title"] == payload["title"]
    assert body["body"] == payload["body"]
    assert body["userId"] == payload["userId"]
    assert isinstance(body["id"], int)


@pytest.mark.positive
def test_update_post_replaces_fields(api_client, base_url, timeout):
    """MOCK-API — PUT /posts/1 replaces post fields and returns updated body."""
    # Arrange
    url = f"{base_url}/posts/1"
    payload = {"id": 1, "title": "Updated title", "body": "Updated body", "userId": 1}

    # Act
    response = api_client.put(url, json=payload, timeout=timeout)

    # Assert
    assert_status(response, 200)
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == payload["title"]
    assert body["body"] == payload["body"]


@pytest.mark.positive
def test_delete_post_succeeds(api_client, base_url, timeout):
    """MOCK-API — DELETE /posts/1 returns success for a mock delete."""
    # Arrange
    url = f"{base_url}/posts/1"

    # Act
    response = api_client.delete(url, timeout=timeout)

    # Assert
    assert response.status_code in (200, 204), (
        f"Expected 200/204, got {response.status_code}: {response.text[:500]}"
    )


@pytest.mark.negative
def test_get_post_not_found_returns_404(api_client, base_url, timeout):
    """MOCK-API — GET /posts/{missing} returns 404 for an unknown id."""
    # Arrange
    url = f"{base_url}/posts/99999"

    # Act
    response = api_client.get(url, timeout=timeout)

    # Assert
    assert_status(response, 404)


@pytest.mark.edge
def test_filter_posts_by_user_id(api_client, base_url, timeout):
    """MOCK-API — GET /posts?userId=1 returns only posts for that user."""
    # Arrange
    user_id = 1
    url = f"{base_url}/posts"
    params = {"userId": user_id}

    # Act
    response = api_client.get(url, params=params, timeout=timeout)

    # Assert
    assert_status(response, 200)
    posts = response.json()
    assert isinstance(posts, list)
    assert len(posts) >= 1
    assert all(post["userId"] == user_id for post in posts)
