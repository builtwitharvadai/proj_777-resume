"""WebSocket connection wrapper with user context and state management."""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionState(str, Enum):
    """WebSocket connection states."""

    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"


class WebSocketConnection:
    """WebSocket connection wrapper with user context and state management.

    Attributes:
        websocket: FastAPI WebSocket instance
        user_id: User UUID associated with this connection
        connection_id: Unique connection identifier
        connection_time: Timestamp when connection was established
        last_ping: Timestamp of last heartbeat ping
        state: Current connection state
        metadata: Additional connection metadata
    """

    def __init__(
        self,
        websocket: WebSocket,
        user_id: UUID,
        connection_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize WebSocket connection wrapper.

        Args:
            websocket: FastAPI WebSocket instance
            user_id: User UUID
            connection_id: Unique connection identifier
            metadata: Optional connection metadata
        """
        self.websocket = websocket
        self.user_id = user_id
        self.connection_id = connection_id
        self.connection_time = datetime.utcnow()
        self.last_ping = datetime.utcnow()
        self.state = ConnectionState.CONNECTING
        self.metadata = metadata or {}

        logger.info(
            "WebSocket connection created",
            extra={
                "user_id": str(user_id),
                "connection_id": connection_id,
                "connection_time": self.connection_time.isoformat(),
            },
        )

    async def accept(self) -> None:
        """Accept the WebSocket connection.

        Raises:
            Exception: If connection acceptance fails
        """
        try:
            await self.websocket.accept()
            self.state = ConnectionState.CONNECTED
            logger.info(
                "WebSocket connection accepted",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                },
            )
        except Exception as exc:
            logger.error(
                "Failed to accept WebSocket connection",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
            self.state = ConnectionState.DISCONNECTED
            raise

    async def send_json(self, data: Dict[str, Any]) -> None:
        """Send JSON message through WebSocket.

        Args:
            data: Data to send as JSON

        Raises:
            Exception: If sending fails
        """
        try:
            await self.websocket.send_json(data)
            logger.debug(
                "WebSocket message sent",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                    "message_type": data.get("type"),
                },
            )
        except Exception as exc:
            logger.error(
                "Failed to send WebSocket message",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

    async def send_text(self, message: str) -> None:
        """Send text message through WebSocket.

        Args:
            message: Text message to send

        Raises:
            Exception: If sending fails
        """
        try:
            await self.websocket.send_text(message)
            logger.debug(
                "WebSocket text sent",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                },
            )
        except Exception as exc:
            logger.error(
                "Failed to send WebSocket text",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

    async def receive_text(self) -> str:
        """Receive text message from WebSocket.

        Returns:
            Received text message

        Raises:
            Exception: If receiving fails
        """
        try:
            message = await self.websocket.receive_text()
            logger.debug(
                "WebSocket text received",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                },
            )
            return message
        except Exception as exc:
            logger.error(
                "Failed to receive WebSocket text",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

    async def receive_json(self) -> Dict[str, Any]:
        """Receive JSON message from WebSocket.

        Returns:
            Received JSON data as dictionary

        Raises:
            Exception: If receiving fails
        """
        try:
            data = await self.websocket.receive_json()
            logger.debug(
                "WebSocket JSON received",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                    "message_type": data.get("type") if isinstance(data, dict) else None,
                },
            )
            return data
        except Exception as exc:
            logger.error(
                "Failed to receive WebSocket JSON",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

    async def close(self, code: int = 1000, reason: str = "Normal closure") -> None:
        """Close the WebSocket connection.

        Args:
            code: WebSocket close code
            reason: Close reason message
        """
        try:
            self.state = ConnectionState.DISCONNECTING
            await self.websocket.close(code=code, reason=reason)
            self.state = ConnectionState.DISCONNECTED
            logger.info(
                "WebSocket connection closed",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                    "code": code,
                    "reason": reason,
                    "duration_seconds": (
                        datetime.utcnow() - self.connection_time
                    ).total_seconds(),
                },
            )
        except Exception as exc:
            logger.error(
                "Failed to close WebSocket connection",
                extra={
                    "user_id": str(self.user_id),
                    "connection_id": self.connection_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
            self.state = ConnectionState.DISCONNECTED

    def update_ping(self) -> None:
        """Update last ping timestamp."""
        self.last_ping = datetime.utcnow()
        logger.debug(
            "WebSocket ping updated",
            extra={
                "user_id": str(self.user_id),
                "connection_id": self.connection_id,
                "last_ping": self.last_ping.isoformat(),
            },
        )

    def is_connected(self) -> bool:
        """Check if connection is in connected state.

        Returns:
            True if connected, False otherwise
        """
        return self.state == ConnectionState.CONNECTED

    def get_connection_duration(self) -> float:
        """Get connection duration in seconds.

        Returns:
            Duration in seconds since connection was established
        """
        return (datetime.utcnow() - self.connection_time).total_seconds()

    def get_time_since_last_ping(self) -> float:
        """Get time since last ping in seconds.

        Returns:
            Seconds since last ping
        """
        return (datetime.utcnow() - self.last_ping).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert connection info to dictionary.

        Returns:
            Dictionary with connection information
        """
        return {
            "user_id": str(self.user_id),
            "connection_id": self.connection_id,
            "connection_time": self.connection_time.isoformat(),
            "last_ping": self.last_ping.isoformat(),
            "state": self.state.value,
            "duration_seconds": self.get_connection_duration(),
            "time_since_last_ping_seconds": self.get_time_since_last_ping(),
            "metadata": self.metadata,
        }
