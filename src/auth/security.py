"""Security utilities for password hashing and JWT token management."""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
import jwt
from pydantic import ValidationError

from src.core.config import settings

logger = logging.getLogger(__name__)

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
VERIFICATION_TOKEN_EXPIRE_HOURS = 24
RESET_TOKEN_EXPIRE_HOURS = 1
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string

    Raises:
        ValueError: If password is empty or invalid
    """
    if not password:
        logger.error("Attempted to hash empty password")
        raise ValueError("Password cannot be empty")

    try:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        logger.debug("Password hashed successfully")
        return hashed.decode("utf-8")
    except Exception as exc:
        logger.error(
            "Password hashing failed",
            extra={"error": str(exc)},
            exc_info=True,
        )
        raise ValueError("Failed to hash password") from exc


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    if not plain_password or not hashed_password:
        logger.warning("Attempted to verify with empty password or hash")
        return False

    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        result = bcrypt.checkpw(password_bytes, hashed_bytes)
        logger.debug(
            "Password verification completed",
            extra={"result": result},
        )
        return result
    except Exception as exc:
        logger.error(
            "Password verification failed",
            extra={"error": str(exc)},
            exc_info=True,
        )
        return False


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    Raises:
        ValueError: If token creation fails
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

        logger.debug(
            "Access token created",
            extra={"expires_at": expire.isoformat()},
        )
        return encoded_jwt
    except Exception as exc:
        logger.error(
            "Access token creation failed",
            extra={"error": str(exc)},
            exc_info=True,
        )
        raise ValueError("Failed to create access token") from exc


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT refresh token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token string

    Raises:
        ValueError: If token creation fails
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

        logger.debug(
            "Refresh token created",
            extra={"expires_at": expire.isoformat()},
        )
        return encoded_jwt
    except Exception as exc:
        logger.error(
            "Refresh token creation failed",
            extra={"error": str(exc)},
            exc_info=True,
        )
        raise ValueError("Failed to create refresh token") from exc


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT token.

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload

    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug("Token decoded successfully")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as exc:
        logger.warning(
            "Invalid token",
            extra={"error": str(exc)},
        )
        raise ValueError("Invalid token") from exc
    except Exception as exc:
        logger.error(
            "Token decoding failed",
            extra={"error": str(exc)},
            exc_info=True,
        )
        raise ValueError("Failed to decode token") from exc


def create_verification_token() -> str:
    """Create a secure random token for email verification.

    Returns:
        Random URL-safe token string
    """
    token = secrets.token_urlsafe(32)
    logger.debug("Verification token created")
    return token


def create_reset_token() -> str:
    """Create a secure random token for password reset.

    Returns:
        Random URL-safe token string
    """
    token = secrets.token_urlsafe(32)
    logger.debug("Reset token created")
    return token


def create_verification_token_with_expiry(email: str) -> str:
    """Create a JWT token for email verification with expiration.

    Args:
        email: User email address

    Returns:
        Encoded JWT token for email verification

    Raises:
        ValueError: If token creation fails
    """
    try:
        expire = datetime.utcnow() + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
        data = {"sub": email, "exp": expire, "type": "email_verification"}
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, algorithm=ALGORITHM)

        logger.debug(
            "Email verification token created",
            extra={"email": email, "expires_at": expire.isoformat()},
        )
        return encoded_jwt
    except Exception as exc:
        logger.error(
            "Email verification token creation failed",
            extra={"error": str(exc)},
            exc_info=True,
        )
        raise ValueError("Failed to create verification token") from exc


def create_reset_token_with_expiry(email: str) -> str:
    """Create a JWT token for password reset with expiration.

    Args:
        email: User email address

    Returns:
        Encoded JWT token for password reset

    Raises:
        ValueError: If token creation fails
    """
    try:
        expire = datetime.utcnow() + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
        data = {"sub": email, "exp": expire, "type": "password_reset"}
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, algorithm=ALGORITHM)

        logger.debug(
            "Password reset token created",
            extra={"email": email, "expires_at": expire.isoformat()},
        )
        return encoded_jwt
    except Exception as exc:
        logger.error(
            "Password reset token creation failed",
            extra={"error": str(exc)},
            exc_info=True,
        )
        raise ValueError("Failed to create reset token") from exc
