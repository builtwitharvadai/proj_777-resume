"""WebSocket authentication utilities for JWT token validation."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import WebSocket, WebSocketException, status

from src.auth import security
from src.database.models.user import User
from src.auth import service
from src.database.connection import get_db

logger = logging.getLogger(__name__)


async def get_token_from_websocket(websocket: WebSocket) -> Optional[str]:
    """Extract JWT token from WebSocket query parameters or headers.

    Args:
        websocket: WebSocket instance

    Returns:
        JWT token if found, None otherwise
    """
    token = websocket.query_params.get("token")
    if token:
        logger.debug("Token extracted from query parameters")
        return token

    auth_header = websocket.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        logger.debug("Token extracted from Authorization header")
        return token

    logger.warning("No token found in query params or headers")
    return None


async def authenticate_websocket(websocket: WebSocket) -> User:
    """Authenticate WebSocket connection and extract user.

    Args:
        websocket: WebSocket instance

    Returns:
        Authenticated user

    Raises:
        WebSocketException: If authentication fails
    """
    token = await get_token_from_websocket(websocket)

    if not token:
        logger.warning("WebSocket authentication failed: No token provided")
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Authentication required",
        )

    try:
        payload = security.decode_token(token)
    except ValueError as exc:
        logger.warning(
            "WebSocket token validation failed",
            extra={"error": str(exc)},
        )
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid authentication token",
        ) from exc

    token_type = payload.get("type")
    if token_type != "access":
        logger.warning(
            "Invalid WebSocket token type",
            extra={"token_type": token_type},
        )
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token type",
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        logger.warning("WebSocket token missing user ID")
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token payload",
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError as exc:
        logger.warning(
            "Invalid user ID format in WebSocket token",
            extra={"user_id": user_id_str},
        )
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid token payload",
        ) from exc

    async for db in get_db():
        try:
            user = await service.get_user_by_id(db, user_id)
            if not user:
                logger.warning(
                    "User not found for WebSocket authentication",
                    extra={"user_id": str(user_id)},
                )
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="User not found",
                )

            logger.info(
                "WebSocket authenticated successfully",
                extra={"user_id": str(user.id), "email": user.email},
            )
            return user
        except WebSocketException:
            raise
        except Exception as exc:
            logger.error(
                "WebSocket authentication error",
                extra={"error": str(exc)},
                exc_info=True,
            )
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason="Authentication error",
            ) from exc

    raise WebSocketException(
        code=status.WS_1011_INTERNAL_ERROR,
        reason="Database connection failed",
    )


async def validate_websocket_message(message: dict, user_id: UUID) -> bool:
    """Validate WebSocket message belongs to authenticated user.

    Args:
        message: Message dictionary
        user_id: Authenticated user UUID

    Returns:
        True if message is valid for user, False otherwise
    """
    message_user_id = message.get("user_id")

    if not message_user_id:
        logger.warning("Message missing user_id")
        return False

    try:
        message_uuid = UUID(message_user_id) if isinstance(message_user_id, str) else message_user_id
        if message_uuid != user_id:
            logger.warning(
                "Message user_id mismatch",
                extra={
                    "authenticated_user": str(user_id),
                    "message_user": str(message_uuid),
                },
            )
            return False
    except (ValueError, TypeError) as exc:
        logger.warning(
            "Invalid user_id in message",
            extra={"error": str(exc)},
        )
        return False

    return True
