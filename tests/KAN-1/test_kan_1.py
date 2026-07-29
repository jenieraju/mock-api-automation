import pytest

@pytest.mark.positive
def test_valid_api_key_returns_200(api_client, api_key, base_url):
    """KAN-1: Verify that providing a valid API key returns HTTP 200 for GET /products."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data

@pytest.mark.negative
def test_missing_api_key_returns_401(api_client, base_url):
    """KAN-1: Ensure that omitting the API key results in an unauthorized error."""
    # Arrange
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url)
    # Assert
    assert response.status_code == 401

@pytest.mark.edge
def test_api_key_with_leading_trailing_spaces_returns_401(api_client, api_key, base_url):
    """KAN-1: Check handling of API key containing whitespace characters."""
    # Arrange
    headers = {"Authorization": f"  {api_key}  "}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 401

@pytest.mark.positive
def test_response_includes_pagination_fields(api_client, api_key, base_url):
    """KAN-1: Validate that the response contains pagination metadata fields."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    for field in ("page", "per_page", "total", "total_pages"):
        assert field in json_body
        assert isinstance(json_body[field], int)

@pytest.mark.negative
def test_non_numeric_pagination_parameter_returns_400(api_client, api_key, base_url):
    """KAN-1: Verify that providing a non‑numeric value for the page query parameter results in a bad request."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products?page=abc"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 400

@pytest.mark.edge
def test_page_parameter_zero_returns_pagination_fields(api_client, api_key, base_url):
    """KAN-1: Test boundary condition where page=0 is requested."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products?page=0"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert "page" in json_body and json_body["page"] == 0
    for field in ("per_page", "total", "total_pages"):
        assert field in json_body

@pytest.mark.positive
def test_product_objects_contain_required_fields(api_client, api_key, base_url):
    """KAN-1: Confirm each product in the response includes id, name, year, color, and pantone_value."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert "data" in json_body
    for product in json_body["data"]:
        assert isinstance(product.get("id"), int)
        assert isinstance(product.get("name"), str)
        assert isinstance(product.get("year"), int)
        assert isinstance(product.get("color"), str)
        assert isinstance(product.get("pantone_value"), str)

@pytest.mark.negative
def test_unsupported_accept_header_returns_406(api_client, api_key, base_url):
    """KAN-1: Ensure that requesting a non‑JSON response format is rejected."""
    # Arrange
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/xml"
    }
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 406

@pytest.mark.edge
def test_product_name_with_special_characters(api_client, api_key, base_url):
    """KAN-1: Validate handling of product names containing Unicode and special symbols."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    for product in json_body.get("data", []):
        name = product.get("name", "")
        assert isinstance(name, str)

@pytest.mark.positive
def test_page_1_returns_first_6_items(api_client, api_key, base_url):
    """KAN-1: Verify that requesting page=1 returns the first six products."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products?page=1&per_page=6"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert "data" in json_body
    assert len(json_body["data"]) == 6

@pytest.mark.positive
def test_page_2_returns_remaining_items(api_client, api_key, base_url):
    """KAN-1: Verify that requesting page=2 returns the remaining products after the first page."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products?page=2&per_page=6"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert "data" in json_body
    # The exact number may vary; ensure it is not the same as page 1
    assert len(json_body["data"]) <= 6

@pytest.mark.negative
def test_out_of_range_page_returns_empty_data(api_client, api_key, base_url):
    """KAN-1: Check that requesting a page number beyond total_pages returns an empty list."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products?page=999&per_page=6"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert "data" in json_body
    assert json_body["data"] == []

@pytest.mark.edge
def test_concurrent_requests_for_page_1_and_page_2(api_client, api_key, base_url):
    """KAN-1: Validate API stability under simultaneous pagination requests."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url1 = f"{base_url}/products?page=1&per_page=6"
    url2 = f"{base_url}/products?page=2&per_page=6"
    # Act
    resp1 = api_client.get(url1, headers=headers)
    resp2 = api_client.get(url2, headers=headers)
    # Assert
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    data1 = resp1.json().get("data", [])
    data2 = resp2.json().get("data", [])
    assert isinstance(data1, list)
    assert isinstance(data2, list)

@pytest.mark.positive
def test_all_product_ids_are_positive_integers(api_client, api_key, base_url):
    """KAN-1: Assert that every product id in the response is a positive integer."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    for product in response.json().get("data", []):
        assert isinstance(product.get("id"), int)
        assert product["id"] > 0

@pytest.mark.negative
def test_product_with_zero_id_returns_500(api_client, api_key, base_url):
    """KAN-1: Simulate a scenario where a product record has an ID of zero and verify server error handling."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 500

@pytest.mark.edge
def test_maximum_integer_id_handled_correctly(api_client, api_key, base_url):
    """KAN-1: Test that a product with the maximum 32‑bit integer ID is processed without overflow."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    ids = [p.get("id") for p in response.json().get("data", [])]
    assert 2147483647 in ids

@pytest.mark.positive
def test_valid_product_color_hex_codes(api_client, api_key, base_url):
    """KAN-1: GET /products returns products where each color field conforms to hex color format #RRGGBB."""
    # Arrange
    headers = {"x-api-key": api_key}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    for product in response.json().get("data", []):
        color = product.get("color", "")
        assert isinstance(color, str)
        assert color.startswith("#")
        assert len(color) == 7
        hex_part = color[1:]
        for ch in hex_part:
            assert ch.lower() in "0123456789abcdef"

@pytest.mark.negative
def test_product_color_field_with_invalid_format(api_client, api_key, base_url):
    """KAN-1: GET /products returns a product whose color field is not a valid hex code."""
    # Arrange
    headers = {"x-api-key": api_key}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    invalid_found = False
    for product in response.json().get("data", []):
        color = product.get("color", "")
        if not (color.startswith("#") and len(color) == 7 and all(c.lower() in "0123456789abcdef" for c in color[1:])):
            invalid_found = True
            break
    assert invalid_found

@pytest.mark.edge
def test_edge_case_empty_color_string(api_client, api_key, base_url):
    """KAN-1: GET /products returns a product where the color field is an empty string."""
    # Arrange
    headers = {"x-api-key": api_key}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    empty_found = any(product.get("color") == "" for product in response.json().get("data", []))
    assert empty_found

@pytest.mark.positive
def test_valid_pantone_value_pattern(api_client, api_key, base_url):
    """KAN-1: GET /products returns products where each pantone_value follows the pattern XX-XXXX."""
    # Arrange
    headers = {"x-api-key": api_key}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    for product in response.json().get("data", []):
        pv = product.get("pantone_value", "")
        parts = pv.split("-")
        assert len(parts) == 2
        assert len(parts[0]) == 2 and parts[0].isdigit()
        assert len(parts[1]) == 4 and parts[1].isdigit()

@pytest.mark.negative
def test_invalid_pantone_value_format(api_client, api_key, base_url):
    """KAN-1: GET /products returns a product with a pantone_value that does not match the required pattern."""
    # Arrange
    headers = {"x-api-key": api_key}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    invalid_found = False
    for product in response.json().get("data", []):
        pv = product.get("pantone_value", "")
        parts = pv.split("-")
        if not (len(parts) == 2 and len(parts[0]) == 2 and parts[0].isdigit() and len(parts[1]) == 4 and parts[1].isdigit()):
            invalid_found = True
            break
    assert invalid_found

@pytest.mark.edge
def test_edge_case_boundary_pantone_value(api_client, api_key, base_url):
    """KAN-1: GET /products returns a product with the minimal valid pantone_value "00-0000"."""
    # Arrange
    headers = {"x-api-key": api_key}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    found = any(product.get("pantone_value") == "00-0000" for product in response.json().get("data", []))
    assert found

@pytest.mark.positive
def test_authorized_request_with_valid_api_key(api_client, api_key, base_url):
    """KAN-1: GET /products with a correct x-api-key header returns product data."""
    # Arrange
    headers = {"x-api-key": api_key}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    assert "data" in response.json()

@pytest.mark.negative
def test_missing_x_api_key_header(api_client, base_url):
    """KAN-1: GET /products without the x-api-key header should be rejected."""
    # Arrange
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url)
    # Assert
    assert response.status_code == 401

@pytest.mark.edge
def test_empty_x_api_key_header_value(api_client, base_url):
    """KAN-1: GET /products with x-api-key header present but empty should be treated as unauthorized."""
    # Arrange
    headers = {"x-api-key": ""}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 401

@pytest.mark.positive
def test_authorized_request_with_valid_api_key_duplicate(api_client, api_key, base_url):
    """KAN-1: GET /products with a correct API key returns product data."""
    # Arrange
    headers = {"x-api-key": api_key}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200

@pytest.mark.negative
def test_invalid_api_key_provided(api_client, base_url):
    """KAN-1: GET /products with an incorrect x-api-key should be rejected."""
    # Arrange
    headers = {"x-api-key": "invalid-key"}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 401

@pytest.mark.edge
def test_api_key_with_special_characters(api_client, base_url):
    """KAN-1: GET /products with an API key containing special characters should be rejected."""
    # Arrange
    headers = {"x-api-key": "!@#$%^&*()"}
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 401

@pytest.mark.positive
def test_valid_pagination_within_total_pages(api_client, api_key, base_url):
    """KAN-1: GET /products with a page number that exists returns a populated data array."""
    # Arrange
    headers = {"x-api-key": api_key}
    url = f"{base_url}/products?page=1"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    assert len(response.json().get("data", [])) > 0

@pytest.mark.edge
def test_page_number_exceeding_total_pages_returns_empty_array(api_client, api_key, base_url):
    """KAN-1: GET /products with a page number greater than total_pages returns an empty data array."""
    # Arrange
    headers = {"x-api-key": api_key}
    url = f"{base_url}/products?page=9999"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 200
    assert response.json().get("data", []) == []

@pytest.mark.negative
def test_non_numeric_page_parameter(api_client, api_key, base_url):
    """KAN-1: GET /products with a non‑numeric page query parameter should be rejected."""
    # Arrange
    headers = {"x-api-key": api_key}
    url = f"{base_url}/products?page=abc"
    # Act
    response = api_client.get(url, headers=headers)
    # Assert
    assert response.status_code == 400

@pytest.mark.positive
def test_valid_per_page_matches_data_count_on_first_page(api_client, api_key, base_url):
    """KAN-1: Verify that when per_page is set to 6, the returned data array contains exactly 6 items for page 1."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    params = {"page": 1, "per_page": 6}
    # Act
    response = api_client.get(url, headers=headers, params=params)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert json_body.get("per_page") == 6
    assert len(json_body.get("data", [])) == 6

@pytest.mark.positive
def test_valid_per_page_matches_data_count_on_second_page(api_client, api_key, base_url):
    """KAN-1: Verify that per_page=6 returns exactly 6 items on page 2 when total products are 12."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    params = {"page": 2, "per_page": 6}
    # Act
    response = api_client.get(url, headers=headers, params=params)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert json_body.get("per_page") == 6
    assert len(json_body.get("data", [])) == 6

@pytest.mark.negative
def test_mismatched_per_page_value_returns_error(api_client, api_key, base_url):
    """KAN-1: Request with per_page=5 but the service returns 6 items, causing a mismatch validation error."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    params = {"page": 1, "per_page": 5}
    # Act
    response = api_client.get(url, headers=headers, params=params)
    # Assert
    assert response.status_code == 400

@pytest.mark.negative
def test_missing_per_page_parameter_results_in_validation_error(api_client, api_key, base_url):
    """KAN-1: Omit the per_page query parameter and expect the API to reject the request due to missing required field."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    params = {"page": 1}
    # Act
    response = api_client.get(url, headers=headers, params=params)
    # Assert
    assert response.status_code == 400

@pytest.mark.edge
def test_zero_per_page_returns_empty_data_array(api_client, api_key, base_url):
    """KAN-1: Set per_page to 0 to test boundary condition; expect an empty data array without error."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    params = {"page": 1, "per_page": 0}
    # Act
    response = api_client.get(url, headers=headers, params=params)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert json_body.get("per_page") == 0
    assert json_body.get("data", []) == []

@pytest.mark.positive
def test_correct_total_field_matches_sum_across_pages_page_1(api_client, api_key, base_url):
    """KAN-1: Validate that the total field equals 12, which is the sum of items across both pages, when requesting page 1."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    params = {"page": 1, "per_page": 6}
    # Act
    response = api_client.get(url, headers=headers, params=params)
    # Assert
    assert response.status_code == 200
    assert response.json().get("total") == 12

@pytest.mark.positive
def test_correct_total_field_matches_sum_across_pages_page_2(api_client, api_key, base_url):
    """KAN-1: Validate that the total field equals 12 when requesting page 2."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    params = {"page": 2, "per_page": 6}
    # Act
    response = api_client.get(url, headers=headers, params=params)
    # Assert
    assert response.status_code == 200
    assert response.json().get("total") == 12

@pytest.mark.negative
def test_incorrect_total_field_triggers_validation_error(api_client, api_key, base_url):
    """KAN-1: API returns a total value of 10 instead of the expected 12, leading to a mismatch error."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    params = {"page": 1, "per_page": 6}
    # Act
    response = api_client.get(url, headers=headers, params=params)
    # Assert
    assert response.status_code == 400

@pytest.mark.negative
def test_missing_total_field_results_in_error(api_client, api_key, base_url):
    """KAN-1: Omit the total field from the response (simulated) and verify the API reports the omission as an error."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    params = {"page": 1, "per_page": 6}
    # Act
    response = api_client.get(url, headers=headers, params=params)
    # Assert
    assert response.status_code == 400

@pytest.mark.edge
def test_excessively_large_total_value_causes_validation_failure(api_client, api_key, base_url):
    """KAN-1: Return a total field with an unrealistically large number (e.g., 1,000,000) to test handling of overflow or mismatch."""
    # Arrange
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{base_url}/products"
    params = {"page": 1, "per_page": 6}
    # Act
    response = api_client.get(url, headers=headers, params=params)
    # Assert
    assert response.status_code == 400

@pytest.mark.positive
def test_retrieve_first_page_of_products_positive(api_client, base_url):
    """KAN-1: Verify that the first page of the product list is returned with total_pages equal to 2."""
    # Arrange
    url = f"{base_url}/products?page=1"
    # Act
    response = api_client.get(url)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert json_body.get("total_pages") == 2
    assert json_body.get("data")

@pytest.mark.edge
def test_retrieve_second_page_of_products_edge(api_client, base_url):
    """KAN-1: Request the last available page to ensure pagination boundaries are handled correctly."""
    # Arrange
    url = f"{base_url}/products?page=2"
    # Act
    response = api_client.get(url)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert json_body.get("total_pages") == 2

@pytest.mark.negative
def test_request_page_beyond_total_pages_negative(api_client, base_url):
    """KAN-1: Attempt to retrieve a page number that exceeds the total number of pages."""
    # Arrange
    url = f"{base_url}/products?page=3"
    # Act
    response = api_client.get(url)
    # Assert
    assert response.status_code in (400, 404)

@pytest.mark.positive
def test_missing_page_parameter_defaults_to_first_page_positive(api_client, base_url):
    """KAN-1: Omit the pagination parameter to verify the API defaults to the first page."""
    # Arrange
    url = f"{base_url}/products"
    # Act
    response = api_client.get(url)
    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert json