"""Shared pytest fixtures for testing the Activities API"""

import copy
import pytest
from fastapi.testclient import TestClient

from src import app as application


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI application"""
    return TestClient(application.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before each test to ensure isolation"""
    # Make a deep copy of the initial activities and restore it
    initial = copy.deepcopy(application.activities)
    # Yield to the test, then restore
    yield
    application.activities.clear()
    application.activities.update(copy.deepcopy(initial))


@pytest.fixture
def sample_email():
    return "student@mergington.edu"


@pytest.fixture
def existing_email():
    return "michael@mergington.edu"


@pytest.fixture
def valid_activity():
    return "Chess Club"


@pytest.fixture
def invalid_activity():
    return "Nonexistent Activity"
