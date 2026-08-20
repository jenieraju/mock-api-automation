import pytest

@pytest.mark.positive
def test_create_user_success(api_client, api_key, base_url):
    """
    KAN-2: Verify that a user is created when all required fields are supplied and a valid API key is provided.
    """
    # Arrange
    endpoint = "/users"
    url = f"{base_url}{endpoint}"
    headers = {"API-Key": api_key}
    payload = {
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }

    # Act
    response = api_client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data.get("email") == payload["email"]
    assert data.get("first_name") == payload["first_name"]
    assert data.get("last_name") == payload["last_name"]


@pytest.mark.negative
def test_create_user_missing_required_fields(api_client, api_key, base_url):
    """
    KAN-2: Verify that the API returns an error when a required field is omitted in the create‑user request.
    """
    # Arrange
    endpoint = "/users"
    url = f"{base_url}{endpoint}"
    headers = {"API-Key": api_key}
    payload = {
        "first_name": "John",
        "last_name": "Doe"
        # "email" is omitted intentionally
    }

    # Act
    response = api_client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code == 400
    # Optionally verify error message contains information about missing fields
    # data = response.json()
    # assert "email" in data.get("error", "")


@pytest.mark.negative
def test_create_user_invalid_api_key(api_client, base_url):
    """
    KAN-2: Verify that a request with an invalid API key is rejected when creating a user.
    """
    # Arrange
    endpoint = "/users"
    url = f"{base_url}{endpoint}"
    headers = {"API-Key": "invalid-key"}
    payload = {
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }

    # Act
    response = api_client.post(url, json=payload, headers=headers)

    # Assert
    assert response.status_code in (401, 403)


@pytest.mark.positive
def test_delete_user_success(api_client, api_key, base_url):
    """
    KAN-2: Verify that an existing user can be deleted successfully with a valid API key.
    """
    # Arrange
    # Step 1: Create a user to obtain a valid ID
    create_endpoint = "/users"
    create_url = f"{base_url}{create_endpoint}"
    headers = {"API-Key": api_key}
    payload = {
        "email": "delete_me@example.com",
        "first_name": "Delete",
        "last_name": "Me"
    }
    create_resp = api_client.post(create_url, json=payload, headers=headers)
    assert create_resp.status_code == 201
    user_id = create_resp.json().get("id")
    assert user_id is not None

    # Step 2: Delete the created user
    delete_endpoint = f"/users/{user_id}"
    delete_url = f"{base_url}{delete_endpoint}"

    # Act
    delete_resp = api_client.delete(delete_url, headers=headers)

    # Assert
    assert delete_resp.status_code == 204


@pytest.mark.negative
def test_delete_user_invalid_user_id(api_client, api_key, base_url):
    """
    KAN-2: Verify that attempting to delete a non‑existent user returns an appropriate error.
    """
    # Arrange
    invalid_user_id = 999999
    endpoint = f"/users/{invalid_user_id}"
    url = f"{base_url}{endpoint}"
    headers = {"API-Key": api_key}

    # Act
    response = api_client.delete(url, headers=headers)

    # Assert
    assert response.status_code == 404