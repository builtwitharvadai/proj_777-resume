"""Unit tests for authentication security utilities."""

import pytest
from datetime import datetime, timedelta

from src.auth import security


class TestPasswordHashing:
    """Test suite for password hashing functions."""

    def test_hash_password_success(self) -> None:
        """Test successful password hashing."""
        password = "TestPassword123!"
        hashed = security.hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_empty_raises_error(self) -> None:
        """Test that hashing empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            security.hash_password("")

    def test_hash_password_different_hashes(self) -> None:
        """Test that same password produces different hashes."""
        password = "TestPassword123!"
        hash1 = security.hash_password(password)
        hash2 = security.hash_password(password)

        assert hash1 != hash2

    def test_verify_password_success(self) -> None:
        """Test successful password verification."""
        password = "TestPassword123!"
        hashed = security.hash_password(password)

        assert security.verify_password(password, hashed) is True

    def test_verify_password_wrong_password(self) -> None:
        """Test password verification with wrong password."""
        password = "TestPassword123!"
        hashed = security.hash_password(password)

        assert security.verify_password("WrongPassword123!", hashed) is False

    def test_verify_password_empty_password(self) -> None:
        """Test password verification with empty password."""
        hashed = security.hash_password("TestPassword123!")

        assert security.verify_password("", hashed) is False

    def test_verify_password_empty_hash(self) -> None:
        """Test password verification with empty hash."""
        assert security.verify_password("TestPassword123!", "") is False


class TestAccessToken:
    """Test suite for JWT access token functions."""

    def test_create_access_token_success(self) -> None:
        """Test successful access token creation."""
        data = {"sub": "user_id", "email": "test@example.com"}
        token = security.create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self) -> None:
        """Test access token creation with custom expiration."""
        data = {"sub": "user_id"}
        expires_delta = timedelta(minutes=15)
        token = security.create_access_token(data, expires_delta)

        assert token is not None
        payload = security.decode_token(token)
        assert payload["type"] == "access"

    def test_decode_access_token_success(self) -> None:
        """Test successful access token decoding."""
        data = {"sub": "user_id", "email": "test@example.com"}
        token = security.create_access_token(data)
        payload = security.decode_token(token)

        assert payload["sub"] == "user_id"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_decode_expired_token_raises_error(self) -> None:
        """Test that decoding expired token raises ValueError."""
        data = {"sub": "user_id"}
        expires_delta = timedelta(seconds=-1)
        token = security.create_access_token(data, expires_delta)

        with pytest.raises(ValueError, match="Token has expired"):
            security.decode_token(token)

    def test_decode_invalid_token_raises_error(self) -> None:
        """Test that decoding invalid token raises ValueError."""
        with pytest.raises(ValueError, match="Invalid token"):
            security.decode_token("invalid_token_string")


class TestRefreshToken:
    """Test suite for JWT refresh token functions."""

    def test_create_refresh_token_success(self) -> None:
        """Test successful refresh token creation."""
        data = {"sub": "user_id", "email": "test@example.com"}
        token = security.create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_with_custom_expiry(self) -> None:
        """Test refresh token creation with custom expiration."""
        data = {"sub": "user_id"}
        expires_delta = timedelta(days=14)
        token = security.create_refresh_token(data, expires_delta)

        assert token is not None
        payload = security.decode_token(token)
        assert payload["type"] == "refresh"

    def test_decode_refresh_token_success(self) -> None:
        """Test successful refresh token decoding."""
        data = {"sub": "user_id", "email": "test@example.com"}
        token = security.create_refresh_token(data)
        payload = security.decode_token(token)

        assert payload["sub"] == "user_id"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "refresh"
        assert "exp" in payload


class TestVerificationToken:
    """Test suite for verification token functions."""

    def test_create_verification_token_success(self) -> None:
        """Test successful verification token creation."""
        token = security.create_verification_token()

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_verification_token_unique(self) -> None:
        """Test that verification tokens are unique."""
        token1 = security.create_verification_token()
        token2 = security.create_verification_token()

        assert token1 != token2

    def test_create_verification_token_with_expiry(self) -> None:
        """Test verification token with expiry creation."""
        email = "test@example.com"
        token = security.create_verification_token_with_expiry(email)

        assert token is not None
        payload = security.decode_token(token)
        assert payload["sub"] == email
        assert payload["type"] == "email_verification"
        assert "exp" in payload


class TestResetToken:
    """Test suite for password reset token functions."""

    def test_create_reset_token_success(self) -> None:
        """Test successful reset token creation."""
        token = security.create_reset_token()

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_reset_token_unique(self) -> None:
        """Test that reset tokens are unique."""
        token1 = security.create_reset_token()
        token2 = security.create_reset_token()

        assert token1 != token2

    def test_create_reset_token_with_expiry(self) -> None:
        """Test reset token with expiry creation."""
        email = "test@example.com"
        token = security.create_reset_token_with_expiry(email)

        assert token is not None
        payload = security.decode_token(token)
        assert payload["sub"] == email
        assert payload["type"] == "password_reset"
        assert "exp" in payload


class TestTokenTypes:
    """Test suite for token type validation."""

    def test_access_token_has_correct_type(self) -> None:
        """Test that access token has correct type field."""
        data = {"sub": "user_id"}
        token = security.create_access_token(data)
        payload = security.decode_token(token)

        assert payload["type"] == "access"

    def test_refresh_token_has_correct_type(self) -> None:
        """Test that refresh token has correct type field."""
        data = {"sub": "user_id"}
        token = security.create_refresh_token(data)
        payload = security.decode_token(token)

        assert payload["type"] == "refresh"

    def test_verification_token_has_correct_type(self) -> None:
        """Test that verification token has correct type field."""
        email = "test@example.com"
        token = security.create_verification_token_with_expiry(email)
        payload = security.decode_token(token)

        assert payload["type"] == "email_verification"

    def test_reset_token_has_correct_type(self) -> None:
        """Test that reset token has correct type field."""
        email = "test@example.com"
        token = security.create_reset_token_with_expiry(email)
        payload = security.decode_token(token)

        assert payload["type"] == "password_reset"
