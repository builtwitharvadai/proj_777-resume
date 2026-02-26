"""Integration tests for authentication API endpoints."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.database.connection import get_db
from src.main import app
from src.auth import security


@pytest.fixture(scope="function")
async def test_db_engine():
    """Create test database engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_session(test_db_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
def client(test_db_session):
    """Create test client with overridden database dependency."""

    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


class TestRegisterEndpoint:
    """Test suite for user registration endpoint."""

    def test_register_success(self, client) -> None:
        """Test successful user registration."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["email_verified"] is False
        assert "id" in data

    def test_register_duplicate_email(self, client) -> None:
        """Test registration with duplicate email fails."""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "AnotherPassword123!",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_register_invalid_email(self, client) -> None:
        """Test registration with invalid email fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_weak_password(self, client) -> None:
        """Test registration with weak password fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLoginEndpoint:
    """Test suite for user login endpoint."""

    def test_login_success(self, client) -> None:
        """Test successful user login."""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client) -> None:
        """Test login with wrong password fails."""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client) -> None:
        """Test login with nonexistent user fails."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "TestPassword123!",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestVerifyEmailEndpoint:
    """Test suite for email verification endpoint."""

    def test_verify_email_success(self, client) -> None:
        """Test successful email verification."""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        token = security.create_verification_token_with_expiry("test@example.com")

        response = client.post(
            "/api/auth/verify-email",
            json={"token": token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email_verified"] is True

    def test_verify_email_invalid_token(self, client) -> None:
        """Test email verification with invalid token fails."""
        response = client.post(
            "/api/auth/verify-email",
            json={"token": "invalid_token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_email_nonexistent_user(self, client) -> None:
        """Test email verification for nonexistent user fails."""
        token = security.create_verification_token_with_expiry(
            "nonexistent@example.com"
        )

        response = client.post(
            "/api/auth/verify-email",
            json={"token": token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestResetPasswordEndpoint:
    """Test suite for password reset endpoint."""

    def test_reset_password_request_success(self, client) -> None:
        """Test password reset request returns success message."""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        response = client.post(
            "/api/auth/reset-password",
            json={"email": "test@example.com"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

    def test_reset_password_nonexistent_user(self, client) -> None:
        """Test password reset for nonexistent user returns generic message."""
        response = client.post(
            "/api/auth/reset-password",
            json={"email": "nonexistent@example.com"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()

    def test_reset_password_confirm_success(self, client) -> None:
        """Test password reset confirmation success."""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        token = security.create_reset_token_with_expiry("test@example.com")

        response = client.post(
            "/api/auth/reset-password/confirm",
            json={
                "token": token,
                "new_password": "NewPassword123!",
            },
        )

        assert response.status_code == status.HTTP_200_OK

        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "NewPassword123!",
            },
        )

        assert login_response.status_code == status.HTTP_200_OK

    def test_reset_password_confirm_invalid_token(self, client) -> None:
        """Test password reset confirmation with invalid token fails."""
        response = client.post(
            "/api/auth/reset-password/confirm",
            json={
                "token": "invalid_token",
                "new_password": "NewPassword123!",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRefreshTokenEndpoint:
    """Test suite for token refresh endpoint."""

    def test_refresh_token_success(self, client) -> None:
        """Test successful token refresh."""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        refresh_token = login_response.json()["refresh_token"]

        response = client.post(
            "/api/auth/refresh-token",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid_token(self, client) -> None:
        """Test token refresh with invalid token fails."""
        response = client.post(
            "/api/auth/refresh-token",
            json={"refresh_token": "invalid_token"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentUserEndpoint:
    """Test suite for get current user endpoint."""

    def test_get_current_user_success(self, client) -> None:
        """Test getting current user info with valid token."""
        client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123!",
            },
        )

        access_token = login_response.json()["access_token"]

        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"

    def test_get_current_user_no_token(self, client) -> None:
        """Test getting current user without token fails."""
        response = client.get("/api/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client) -> None:
        """Test getting current user with invalid token fails."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
