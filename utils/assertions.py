"""Reusable response assertions for API tests."""

from __future__ import annotations

from typing import Any, Iterable

import requests


def assert_status(response: requests.Response, expected: int) -> None:
    """Assert HTTP status code with body context on failure."""
    assert response.status_code == expected, (
        f"Expected {expected}, got {response.status_code}: {response.text[:500]}"
    )


def assert_json_keys(payload: dict[str, Any], required: Iterable[str]) -> None:
    """Assert that all required keys exist in a JSON object."""
    missing = [key for key in required if key not in payload]
    assert not missing, f"Missing keys {missing} in payload keys {list(payload)}"
