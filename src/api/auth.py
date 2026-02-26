"""Authentication API endpoints for user registration, login, and management."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import dependencies, schemas, security, service
from src.database.connection import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_create: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
) -> schemas.UserResponse:
    """Register a new user.

    Args:
        user_create: User registration data
        db: Database session

    Returns:
        Created user information

    Raises:
        HTTPException: If user already exists or creation fails
    """
    logger.info(
        "User registration attempt",
        extra={"email": user_create.email},
    )

    try:
        user = await service.create_user(db, user_create)
        logger.info(
            "User registered successfully",
            extra={"user_id": str(user.id), "email": user.email},
        )
        return schemas.UserResponse(
            id=user.id,
            email=user.email,
            email_verified=user.email_verified,
        )
    except ValueError as exc:
        logger.warning(
            "User registration failed",
            extra={"email": user_create.email, "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    user_login: schemas.UserLogin,
    db: AsyncSession = Depends(get_db),
) -> schemas.TokenResponse:
    """Authenticate user and return access tokens.

    Args:
        user_login: User login credentials
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    logger.info(
        "User login attempt",
        extra={"email": user_login.email},
    )

    user = await service.authenticate_user(db, user_login.email, user_login.password)
    if not user:
        logger.warning(
            "Login failed: invalid credentials",
            extra={"email": user_login.email},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        tokens = service.create_tokens_for_user(user)
        logger.info(
            "User logged in successfully",
            extra={"user_id": str(user.id), "email": user.email},
        )
        return tokens
    except ValueError as exc:
        logger.error(
            "Token creation failed during login",
            extra={"user_id": str(user.id), "error": str(exc)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create authentication tokens",
        ) from exc


@router.post("/verify-email", response_model=schemas.UserResponse)
async def verify_email(
    verification: schemas.EmailVerification,
    db: AsyncSession = Depends(get_db),
) -> schemas.UserResponse:
    """Verify user email address with token.

    Args:
        verification: Email verification token
        db: Database session

    Returns:
        Updated user information

    Raises:
        HTTPException: If verification fails
    """
    logger.info("Email verification attempt")

    try:
        payload = security.decode_token(verification.token)
    except ValueError as exc:
        logger.warning(
            "Email verification failed: invalid token",
            extra={"error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        ) from exc

    token_type = payload.get("type")
    if token_type != "email_verification":
        logger.warning(
            "Email verification failed: invalid token type",
            extra={"token_type": token_type},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    email = payload.get("sub")
    if not email:
        logger.warning("Email verification failed: missing email in token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    user = await service.get_user_by_email(db, email)
    if not user:
        logger.warning(
            "Email verification failed: user not found",
            extra={"email": email},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.email_verified:
        logger.info(
            "Email already verified",
            extra={"user_id": str(user.id), "email": email},
        )
        return schemas.UserResponse(
            id=user.id,
            email=user.email,
            email_verified=user.email_verified,
        )

    try:
        user = await service.verify_user_email(db, user)
        logger.info(
            "Email verified successfully",
            extra={"user_id": str(user.id), "email": user.email},
        )
        return schemas.UserResponse(
            id=user.id,
            email=user.email,
            email_verified=user.email_verified,
        )
    except ValueError as exc:
        logger.error(
            "Email verification failed",
            extra={"email": email, "error": str(exc)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email",
        ) from exc


@router.post("/reset-password")
async def reset_password(
    password_reset: schemas.PasswordReset,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Request password reset token.

    Args:
        password_reset: Password reset request data
        db: Database session

    Returns:
        Success message
    """
    logger.info(
        "Password reset request",
        extra={"email": password_reset.email},
    )

    user = await service.get_user_by_email(db, password_reset.email)
    if not user:
        logger.info(
            "Password reset requested for non-existent user",
            extra={"email": password_reset.email},
        )
        return {"message": "If the email exists, a reset link will be sent"}

    try:
        reset_token = security.create_reset_token_with_expiry(user.email)
        logger.info(
            "Password reset token created",
            extra={"user_id": str(user.id), "email": user.email},
        )
        return {"message": "If the email exists, a reset link will be sent"}
    except ValueError as exc:
        logger.error(
            "Password reset token creation failed",
            extra={"email": password_reset.email, "error": str(exc)},
            exc_info=True,
        )
        return {"message": "If the email exists, a reset link will be sent"}


@router.post("/reset-password/confirm", response_model=schemas.UserResponse)
async def reset_password_confirm(
    reset_confirm: schemas.PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
) -> schemas.UserResponse:
    """Confirm password reset with token and new password.

    Args:
        reset_confirm: Password reset confirmation data
        db: Database session

    Returns:
        Updated user information

    Raises:
        HTTPException: If reset fails
    """
    logger.info("Password reset confirmation attempt")

    try:
        payload = security.decode_token(reset_confirm.token)
    except ValueError as exc:
        logger.warning(
            "Password reset failed: invalid token",
            extra={"error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        ) from exc

    token_type = payload.get("type")
    if token_type != "password_reset":
        logger.warning(
            "Password reset failed: invalid token type",
            extra={"token_type": token_type},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    email = payload.get("sub")
    if not email:
        logger.warning("Password reset failed: missing email in token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    user = await service.get_user_by_email(db, email)
    if not user:
        logger.warning(
            "Password reset failed: user not found",
            extra={"email": email},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        user = await service.update_user_password(db, user, reset_confirm.new_password)
        logger.info(
            "Password reset successful",
            extra={"user_id": str(user.id), "email": user.email},
        )
        return schemas.UserResponse(
            id=user.id,
            email=user.email,
            email_verified=user.email_verified,
        )
    except ValueError as exc:
        logger.error(
            "Password reset failed",
            extra={"email": email, "error": str(exc)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password",
        ) from exc


@router.post("/refresh-token", response_model=schemas.TokenResponse)
async def refresh_token(
    token_refresh: schemas.TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> schemas.TokenResponse:
    """Refresh access token using refresh token.

    Args:
        token_refresh: Token refresh request with refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If token refresh fails
    """
    logger.info("Token refresh attempt")

    try:
        payload = security.decode_token(token_refresh.refresh_token)
    except ValueError as exc:
        logger.warning(
            "Token refresh failed: invalid token",
            extra={"error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    token_type = payload.get("type")
    if token_type != "refresh":
        logger.warning(
            "Token refresh failed: invalid token type",
            extra={"token_type": token_type},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        logger.warning("Token refresh failed: missing user ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        from uuid import UUID

        user_id = UUID(user_id_str)
    except ValueError as exc:
        logger.warning(
            "Token refresh failed: invalid user ID format",
            extra={"user_id": user_id_str},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await service.get_user_by_id(db, user_id)
    if not user:
        logger.warning(
            "Token refresh failed: user not found",
            extra={"user_id": str(user_id)},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        tokens = service.create_tokens_for_user(user)
        logger.info(
            "Token refreshed successfully",
            extra={"user_id": str(user.id)},
        )
        return tokens
    except ValueError as exc:
        logger.error(
            "Token refresh failed",
            extra={"user_id": str(user.id), "error": str(exc)},
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token",
        ) from exc


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
) -> schemas.UserResponse:
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user information
    """
    logger.debug(
        "Current user info requested",
        extra={"user_id": str(current_user.id)},
    )
    return current_user
