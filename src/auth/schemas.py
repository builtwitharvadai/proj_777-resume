"""Pydantic schemas for authentication requests and responses."""

import re
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Schema for user registration request.

    Attributes:
        email: Valid email address
        password: Password with minimum security requirements
    """

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements.

        Args:
            v: Password string to validate

        Returns:
            Validated password

        Raises:
            ValueError: If password does not meet requirements
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserLogin(BaseModel):
    """Schema for user login request.

    Attributes:
        email: User email address
        password: User password
    """

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Schema for user response.

    Attributes:
        id: User UUID
        email: User email address
        email_verified: Email verification status
    """

    id: UUID = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email address")
    email_verified: bool = Field(..., description="Email verification status")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for authentication token response.

    Attributes:
        access_token: JWT access token
        token_type: Token type (always 'bearer')
        refresh_token: Optional JWT refresh token
    """

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")


class PasswordReset(BaseModel):
    """Schema for password reset request.

    Attributes:
        email: User email address
    """

    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation.

    Attributes:
        token: Password reset token
        new_password: New password
    """

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements.

        Args:
            v: Password string to validate

        Returns:
            Validated password

        Raises:
            ValueError: If password does not meet requirements
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class EmailVerification(BaseModel):
    """Schema for email verification.

    Attributes:
        token: Email verification token
    """

    token: str = Field(..., description="Email verification token")


class TokenRefresh(BaseModel):
    """Schema for token refresh request.

    Attributes:
        refresh_token: JWT refresh token
    """

    refresh_token: str = Field(..., description="JWT refresh token")
