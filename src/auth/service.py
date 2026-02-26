"""Authentication service for user management and authentication operations."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import schemas, security
from src.database.models.user import User

logger = logging.getLogger(__name__)


async def create_user(
    db: AsyncSession,
    user_create: schemas.UserCreate,
) -> User:
    """Create a new user with hashed password.

    Args:
        db: Database session
        user_create: User creation schema with email and password

    Returns:
        Created user instance

    Raises:
        ValueError: If user with email already exists or creation fails
    """
    logger.info(
        "Creating new user",
        extra={"email": user_create.email},
    )

    existing_user = await get_user_by_email(db, user_create.email)
    if existing_user:
        logger.warning(
            "User already exists",
            extra={"email": user_create.email},
        )
        raise ValueError("User with this email already exists")

    try:
        hashed_password = security.hash_password(user_create.password)

        user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            email_verified=False,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(
            "User created successfully",
            extra={"user_id": str(user.id), "email": user.email},
        )
        return user
    except Exception as exc:
        await db.rollback()
        logger.error(
            "User creation failed",
            extra={"email": user_create.email, "error": str(exc)},
            exc_info=True,
        )
        raise ValueError("Failed to create user") from exc


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email address.

    Args:
        db: Database session
        email: User email address

    Returns:
        User instance if found, None otherwise
    """
    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            logger.debug(
                "User found by email",
                extra={"user_id": str(user.id), "email": email},
            )
        else:
            logger.debug(
                "No user found with email",
                extra={"email": email},
            )

        return user
    except Exception as exc:
        logger.error(
            "Failed to get user by email",
            extra={"email": email, "error": str(exc)},
            exc_info=True,
        )
        return None


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user by ID.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        User instance if found, None otherwise
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user:
            logger.debug(
                "User found by ID",
                extra={"user_id": str(user_id)},
            )
        else:
            logger.debug(
                "No user found with ID",
                extra={"user_id": str(user_id)},
            )

        return user
    except Exception as exc:
        logger.error(
            "Failed to get user by ID",
            extra={"user_id": str(user_id), "error": str(exc)},
            exc_info=True,
        )
        return None


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> Optional[User]:
    """Authenticate user with email and password.

    Args:
        db: Database session
        email: User email address
        password: Plain text password

    Returns:
        User instance if authentication successful, None otherwise
    """
    logger.info(
        "Authenticating user",
        extra={"email": email},
    )

    user = await get_user_by_email(db, email)
    if not user:
        logger.warning(
            "Authentication failed: user not found",
            extra={"email": email},
        )
        return None

    if not security.verify_password(password, user.hashed_password):
        logger.warning(
            "Authentication failed: invalid password",
            extra={"email": email, "user_id": str(user.id)},
        )
        return None

    logger.info(
        "User authenticated successfully",
        extra={"user_id": str(user.id), "email": email},
    )
    return user


async def verify_user_email(db: AsyncSession, user: User) -> User:
    """Mark user email as verified.

    Args:
        db: Database session
        user: User instance to verify

    Returns:
        Updated user instance

    Raises:
        ValueError: If verification fails
    """
    logger.info(
        "Verifying user email",
        extra={"user_id": str(user.id), "email": user.email},
    )

    try:
        user.email_verified = True
        await db.commit()
        await db.refresh(user)

        logger.info(
            "Email verified successfully",
            extra={"user_id": str(user.id), "email": user.email},
        )
        return user
    except Exception as exc:
        await db.rollback()
        logger.error(
            "Email verification failed",
            extra={"user_id": str(user.id), "error": str(exc)},
            exc_info=True,
        )
        raise ValueError("Failed to verify email") from exc


async def update_user_password(
    db: AsyncSession,
    user: User,
    new_password: str,
) -> User:
    """Update user password.

    Args:
        db: Database session
        user: User instance to update
        new_password: New plain text password

    Returns:
        Updated user instance

    Raises:
        ValueError: If password update fails
    """
    logger.info(
        "Updating user password",
        extra={"user_id": str(user.id), "email": user.email},
    )

    try:
        hashed_password = security.hash_password(new_password)
        user.hashed_password = hashed_password

        await db.commit()
        await db.refresh(user)

        logger.info(
            "Password updated successfully",
            extra={"user_id": str(user.id), "email": user.email},
        )
        return user
    except Exception as exc:
        await db.rollback()
        logger.error(
            "Password update failed",
            extra={"user_id": str(user.id), "error": str(exc)},
            exc_info=True,
        )
        raise ValueError("Failed to update password") from exc


def create_tokens_for_user(user: User) -> schemas.TokenResponse:
    """Create access and refresh tokens for user.

    Args:
        user: User instance

    Returns:
        TokenResponse with access and refresh tokens

    Raises:
        ValueError: If token creation fails
    """
    logger.debug(
        "Creating tokens for user",
        extra={"user_id": str(user.id), "email": user.email},
    )

    try:
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = security.create_access_token(token_data)
        refresh_token = security.create_refresh_token(token_data)

        logger.info(
            "Tokens created successfully",
            extra={"user_id": str(user.id)},
        )

        return schemas.TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
    except Exception as exc:
        logger.error(
            "Token creation failed",
            extra={"user_id": str(user.id), "error": str(exc)},
            exc_info=True,
        )
        raise ValueError("Failed to create tokens") from exc
