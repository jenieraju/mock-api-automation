import re
import pytest


@pytest.mark.positive
def test_get_products_returns_paginated_product_list_with_valid_api_key(api_client, api_key, base_url):
    """KAN-1: Verify that a GET request to /products with a valid API key returns a 200 response,
    includes required pagination fields, and provides correctly paginated product objects with required attributes and positive integer IDs."""
    # Arrange
    endpoint = "/products"
    url = f"{base_url}{endpoint}"
    headers = {"x-api-key": api_key}
    params = {"page": 1, "per_page": 6}

    # Act
    response = api_client.get(url, headers=headers, params=params)

    # Assert
    assert response.status_code == 200
    json_body = response.json()
    for field in ("page", "per_page", "total", "total_pages", "data"):
        assert field in json_body
    assert json_body["page"] == 1
    assert json_body["per_page"] == 6
    assert isinstance(json_body["data"], list)
    assert len(json_body["data"]) == 6
    for product in json_body["data"]:
        for key in ("id", "name", "year", "color", "pantone_value"):
            assert key in product
        assert isinstance(product["id"], int) and product["id"] > 0


@pytest.mark.positive
def test_validate_product_color_hex_code_format(api_client, api_key, base_url):
    """KAN-1: Ensure each product's color field in the response conforms to a valid hex color code (e.g., #A1B2C3)."""
    # Arrange
    endpoint = "/products"
    url = f"{base_url}{endpoint}"
    headers = {"x-api-key": api_key}
    params = {"page": 1, "per_page": 12}
    hex_pattern = re.compile(r"^#([A-Fa-f0-9]{6})$")

    # Act
    response = api_client.get(url, headers=headers, params=params)

    # Assert
    assert response.status_code == 200
    data = response.json().get("data", [])
    for product in data:
        color = product.get("color", "")
        assert hex_pattern.match(color), f"Invalid color format: {color}"


@pytest.mark.positive
def test_validate_product_pantone_value_pattern(api_client, api_key, base_url):
    """KAN-1: Check that each product's pantone_value follows the pattern XX-XXXX (two uppercase letters, a hyphen, four digits)."""
    # Arrange
    endpoint = "/products"
    url = f"{base_url}{endpoint}"
    headers = {"x-api-key": api_key}
    params = {"page": 1, "per_page": 12}
    pantone_pattern = re.compile(r"^[A-Z]{2}-\d{4}$")

    # Act
    response = api_client.get(url, headers=headers, params=params)

    # Assert
    assert response.status_code == 200
    data = response.json().get("data", [])
    for product in data:
        pantone = product.get("pantone_value", "")
        assert pantone_pattern.match(pantone), f"Invalid pantone_value format: {pantone}"


@pytest.mark.negative
def test_missing_x_api_key_header_returns_401(api_client, base_url):
    """KAN-1: The API must reject requests that do not include the required authentication header."""
    # Arrange
    endpoint = "/products"
    url = f"{base_url}{endpoint}"
    params = {"page": 1, "per_page": 6}

    # Act
    response = api_client.get(url, params=params)

    # Assert
    assert response.status_code == 401


@pytest.mark.negative
def test_invalid_x_api_key_value_returns_401(api_client, base_url):
    """KAN-1: The API must reject requests that provide an invalid API key."""
    # Arrange
    endpoint = "/products"
    url = f"{base_url}{endpoint}"
    headers = {"x-api-key": "invalid-key"}
    params = {"page": 1, "per_page": 6}

    # Act
    response = api_client.get(url, headers=headers, params=params)

    # Assert
    assert response.status_code == 401


@pytest.mark.edge
def test_page_number_exceeding_total_pages_returns_empty_data_array(api_client, api_key, base_url):
    """KAN-1: When the requested page number is greater than the total number of pages, the API should return an empty list of products."""
    # Arrange
    endpoint = "/products"
    url = f"{base_url}{endpoint}"
    headers = {"x-api-key": api_key}
    params = {"page": 9999, "per_page": 6}

    # Act
    response = api_client.get(url, headers=headers, params=params)

    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert "data" in json_body
    assert isinstance(json_body["data"], list)
    assert len(json_body["data"]) == 0


@pytest.mark.positive
def test_get_products_verify_per_page_count_and_total_across_pages(api_client, api_key, base_url):
    """KAN-1: Ensure that the response for a valid request returns a data array whose length matches the per_page parameter and that the total field reflects the total number of products across all pages."""
    # Arrange
    endpoint = "/products"
    url = f"{base_url}{endpoint}"
    headers = {"x-api-key": api_key}
    params = {"page": 1, "per_page": 6}

    # Act
    response = api_client.get(url, headers=headers, params=params)

    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert json_body.get("per_page") == 6
    assert json_body.get("total") == 12
    data = json_body.get("data", [])
    assert isinstance(data, list)
    assert len(data) == 6


@pytest.mark.positive
def test_retrieve_product_list_with_pagination_and_verify_sample_product(api_client, api_key, base_url):
    """KAN-1: Verify that a GET request to the products endpoint returns a paginated response with exactly two total pages and includes the expected sample product with correct attribute values."""
    # Arrange
    endpoint = "/products"
    url = f"{base_url}{endpoint}"
    headers = {"x-api-key": api_key}
    params = {"page": 1, "per_page": 12}

    # Act
    response = api_client.get(url, headers=headers, params=params)

    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert json_body.get("total_pages") == 2
    data = json_body.get("data", [])
    sample = next((p for p in data if p.get("id") == 1), None)
    assert sample is not None, "Sample product with id=1 not found"
    assert sample.get("name") == "cerulean"
    assert sample.get("year") == 2000
    assert sample.get("color") == "#98B2D1"
    assert sample.get("pantone_value") == "15-4020"