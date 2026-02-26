"""Rate limiting dependency for document upload endpoints."""

import logging
from typing import Any

from fastapi import HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)


def get_user_identifier(request: Request) -> str:
    """Get user identifier for rate limiting.

    Extracts user ID from request state if authenticated, otherwise
    falls back to remote address.

    Args:
        request: FastAPI request object

    Returns:
        str: User identifier for rate limiting
    """
    # Try to get authenticated user ID from request state
    if hasattr(request.state, "user_id"):
        user_id = request.state.user_id
        logger.debug(
            "Using user ID for rate limiting",
            extra={
                "user_id": user_id,
            },
        )
        return f"user:{user_id}"

    # Fall back to remote address for unauthenticated requests
    remote_addr = get_remote_address(request)
    logger.debug(
        "Using remote address for rate limiting",
        extra={
            "remote_addr": remote_addr,
        },
    )
    return f"ip:{remote_addr}"


# Initialize rate limiter with custom key function
limiter = Limiter(key_func=get_user_identifier)


def rate_limit_exceeded_handler(request: Request, exc: Any) -> None:
    """Handle rate limit exceeded errors.

    Args:
        request: FastAPI request object
        exc: Rate limit exception

    Raises:
        HTTPException: 429 Too Many Requests
    """
    logger.warning(
        "Rate limit exceeded",
        extra={
            "path": request.url.path,
            "method": request.method,
            "identifier": get_user_identifier(request),
        },
    )

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "message": "Too many upload requests. Please try again later.",
        },
    )


# Upload rate limit: 10 requests per minute per user
UPLOAD_RATE_LIMIT = "10/minute"
