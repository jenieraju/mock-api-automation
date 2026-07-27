"""
Shared REST fixtures for mock API automation tests.
"""

from __future__ import annotations

import pytest
import requests

from config.settings import get_settings


@pytest.fixture(scope="session")
def settings():
    return get_settings()


@pytest.fixture(scope="session")
def api_client() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
    return session


@pytest.fixture(scope="session")
def base_url(settings) -> str:
    return settings.api_base_url


@pytest.fixture(scope="session")
def timeout(settings) -> int:
    return settings.api_timeout
