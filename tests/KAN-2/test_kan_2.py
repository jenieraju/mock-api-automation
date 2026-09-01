import pytest

@pytest.mark.positive
def test_create_user_success(api_client, api_key, base_url):
    """KAN-2: Create User - Success - Create a new user by providing all required fields with a valid API key; expect a 201 Created response containing the new user ID."""
    # Arrange
    endpoint = "/users"
    url = f"{base_url}{endpoint}"
    headers = {"X-API-Key": api_key}
    payload = {
        "email": "test.user@example.com",
        "first_name": "Test",
        "last_name": "User"
    }

    # Act
    response = api_client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)


@pytest.mark.negative
def test_create_user_missing_required_field(api_client, api_key, base_url):
    """KAN-2: Create User - Missing Required Field - Attempt to create a user while omitting a required field (e.g., email); the service should reject the request."""
    # Arrange
    endpoint = "/users"
    url = f"{base_url}{endpoint}"
    headers = {"X-API-Key": api_key}
    payload = {
        "first_name": "Test",
        "last_name": "User"
    }

    # Act
    response = api_client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "error" in data or "message" in data


@pytest.mark.negative
def test_create_user_invalid_api_key(api_client, base_url):
    """KAN-2: Create User - Invalid API Key - Use an invalid or absent API key when creating a user; the request should be denied due to authentication failure."""
    # Arrange
    endpoint = "/users"
    url = f"{base_url}{endpoint}"
    headers = {"X-API-Key": "invalid-key"}
    payload = {
        "email": "test.user@example.com",
        "first_name": "Test",
        "last_name": "User"
    }

    # Act
    response = api_client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code in (401, 403)
    data = response.json()
    assert "error" in data or "message" in data


@pytest.mark.positive
def test_delete_user_success(api_client, api_key, base_url):
    """KAN-2: Delete User - Success - Delete an existing user using a valid user ID and API key; expect a successful deletion response."""
    # Arrange: create a user to obtain a valid ID
    create_url = f"{base_url}/users"
    headers = {"X-API-Key": api_key}
    create_payload = {
        "email": "temp.user@example.com",
        "first_name": "Temp",
        "last_name": "User"
    }
    create_resp = api_client.post(create_url, json=create_payload, headers=headers)
    assert create_resp.status_code == 201
    user_id = create_resp.json().get("id")
    assert user_id is not None

    delete_url = f"{base_url}/users/{user_id}"

    # Act
    delete_resp = api_client.delete(delete_url, headers=headers)

    # Assert
    assert delete_resp.status_code == 204


@pytest.mark.negative
def test_delete_user_invalid_user_id(api_client, api_key, base_url):
    """KAN-2: Delete User - Invalid User ID - Attempt to delete a user with a non‑existent user ID; the service should respond with a not‑found error."""
    # Arrange
    invalid_id = 999999
    delete_url = f"{base_url}/users/{invalid_id}"
    headers = {"X-API-Key": api_key}

    # Act
    response = api_client.delete(delete_url, headers=headers)

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "error" in data or "message" in data