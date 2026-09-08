import pytest

@pytest.mark.positive
def test_create_user_successful(api_client, api_key, base_url):
    """
    KAN-2: Create User - Successful
    Create a new user with all required fields using a valid API key.
    """
    # Arrange
    endpoint = "/users"
    url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }

    # Act
    response = api_client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == payload["email"]
    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]


@pytest.mark.negative
def test_create_user_missing_required_fields(api_client, api_key, base_url):
    """
    KAN-2: Create User - Missing Required Fields
    Attempt to create a user while omitting a required field (email).
    """
    # Arrange
    endpoint = "/users"
    url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "first_name": "Test",
        "last_name": "User"
    }

    # Act
    response = api_client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 400
    # Optionally check for an error message in the response body
    # error = response.json()
    # assert "error" in error


@pytest.mark.negative
def test_create_user_invalid_api_key(api_client, base_url):
    """
    KAN-2: Create User - Invalid API Key
    Attempt to create a user using an invalid or missing API key.
    """
    # Arrange
    endpoint = "/users"
    url = f"{base_url}{endpoint}"
    # No valid API key provided; using an obviously invalid token
    headers = {"Authorization": "Bearer invalid_key"}
    payload = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }

    # Act
    response = api_client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code in (401, 403)


@pytest.mark.positive
def test_delete_user_successful(api_client, api_key, base_url):
    """
    KAN-2: Delete User - Successful
    Delete an existing user by providing a valid user ID and API key.
    """
    # Arrange: create a user to obtain a valid ID
    create_endpoint = "/users"
    create_url = f"{base_url}{create_endpoint}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "email": "todelete@example.com",
        "first_name": "ToDelete",
        "last_name": "User"
    }
    create_resp = api_client.post(create_url, json=payload, headers=headers)
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    # Act: delete the created user
    delete_endpoint = f"/users/{user_id}"
    delete_url = f"{base_url}{delete_endpoint}"
    delete_resp = api_client.delete(delete_url, headers=headers)

    # Assert
    assert delete_resp.status_code == 204


@pytest.mark.negative
def test_delete_user_invalid_user_id(api_client, api_key, base_url):
    """
    KAN-2: Delete User - Invalid User ID
    Attempt to delete a user with a non‑existent or malformed user ID.
    """
    # Arrange
    invalid_user_id = 999999
    endpoint = f"/users/{invalid_user_id}"
    url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Act
    response = api_client.delete(url, headers=headers)

    # Assert
    assert response.status_code == 404
    # Optionally verify error details
    # error = response.json()
    # assert "error" in error