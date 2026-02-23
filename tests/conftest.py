"""
Shared fixtures for the Mergington High School API test suite.
"""

import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    """Return a TestClient for the FastAPI app."""
    return TestClient(app, follow_redirects=False)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Snapshot the in-memory activities store before each test and restore it
    afterward, preventing state from leaking between tests.
    """
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)
