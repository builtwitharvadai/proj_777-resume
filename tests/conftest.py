"""Pytest configuration and shared fixtures for testing."""

import os
import pytest
from typing import Generator


@pytest.fixture(scope="session")
def test_environment() -> Generator[None, None, None]:
    """Set up test environment variables."""
    original_env = os.environ.copy()

    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "True"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["SECRET_KEY"] = "test-secret-key-do-not-use-in-production"

    yield

    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="function")
def test_db() -> Generator[None, None, None]:
    """Create a test database and clean up after tests."""
    test_db_path = "./test.db"

    yield

    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture(scope="function")
def test_data_dir(tmp_path) -> str:
    """Create a temporary directory for test data."""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return str(test_dir)


@pytest.fixture(scope="function")
def sample_user_data() -> dict:
    """Provide sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    }


@pytest.fixture(scope="function")
def sample_document_data() -> dict:
    """Provide sample document data for testing."""
    return {
        "title": "Test Resume",
        "content": "This is a test resume content",
        "document_type": "resume",
    }
