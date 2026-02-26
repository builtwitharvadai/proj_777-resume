"""Unit tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI application.

    Returns:
        TestClient instance
    """
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check_returns_200(self, client: TestClient) -> None:
        """Test that health check returns 200 OK status code."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_response_format(self, client: TestClient) -> None:
        """Test that health check returns correct response format."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data

        assert data["status"] == "healthy"
        assert isinstance(data["timestamp"], (int, float))
        assert isinstance(data["version"], str)

    def test_health_check_response_fields(self, client: TestClient) -> None:
        """Test that health check response contains expected fields."""
        response = client.get("/health")
        data = response.json()

        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["timestamp"] > 0


class TestReadyEndpoint:
    """Tests for /ready endpoint."""

    def test_ready_check_returns_200(self, client: TestClient) -> None:
        """Test that readiness check returns 200 OK status code."""
        response = client.get("/ready")
        assert response.status_code == 200

    def test_ready_check_response_format(self, client: TestClient) -> None:
        """Test that readiness check returns correct response format."""
        response = client.get("/ready")
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data

        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], (int, float))
        assert isinstance(data["checks"], dict)

    def test_ready_check_includes_system_info(self, client: TestClient) -> None:
        """Test that readiness check includes system information."""
        response = client.get("/ready")
        data = response.json()

        assert "system" in data["checks"]
        system_info = data["checks"]["system"]

        assert "status" in system_info
        assert "platform" in system_info
        assert "python_version" in system_info

        assert system_info["status"] == "ready"

    def test_ready_check_includes_database_check(self, client: TestClient) -> None:
        """Test that readiness check includes database connectivity check."""
        response = client.get("/ready")
        data = response.json()

        assert "database" in data["checks"]
        database_check = data["checks"]["database"]

        assert "status" in database_check
        assert "message" in database_check

        assert database_check["status"] in ["ready", "not_ready"]

    def test_ready_check_overall_status(self, client: TestClient) -> None:
        """Test that readiness check overall status reflects dependency checks."""
        response = client.get("/ready")
        data = response.json()

        database_status = data["checks"]["database"]["status"]

        if database_status == "ready":
            assert data["status"] == "ready"
        else:
            assert data["status"] == "not_ready"

    def test_ready_check_timestamp_valid(self, client: TestClient) -> None:
        """Test that readiness check timestamp is valid and recent."""
        import time

        before_request = time.time()
        response = client.get("/ready")
        after_request = time.time()

        data = response.json()
        timestamp = data["timestamp"]

        assert before_request <= timestamp <= after_request
