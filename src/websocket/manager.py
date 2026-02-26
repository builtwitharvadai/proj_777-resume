"""WebSocket connection pool manager with Redis pub/sub integration."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

import redis.asyncio as aioredis

from src.core.config import settings
from src.websocket.connection import WebSocketConnection

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket connection pool manager with Redis pub/sub.

    Manages active WebSocket connections, broadcasts messages, and integrates
    with Redis pub/sub for multi-instance message distribution.

    Attributes:
        connections: Dictionary mapping connection IDs to WebSocketConnection instances
        user_connections: Dictionary mapping user IDs to sets of connection IDs
        redis: Redis client for pub/sub
        pubsub: Redis pub/sub instance
        channel_name: Redis pub/sub channel name
        heartbeat_task: Background task for heartbeat monitoring
        pubsub_task: Background task for pub/sub message handling
    """

    def __init__(self, channel_name: str = "websocket_messages"):
        """Initialize WebSocket manager.

        Args:
            channel_name: Redis pub/sub channel name
        """
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[UUID, Set[str]] = {}
        self.redis: Optional[aioredis.Redis] = None
        self.pubsub: Optional[aioredis.client.PubSub] = None
        self.channel_name = channel_name
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.pubsub_task: Optional[asyncio.Task] = None
        logger.info("WebSocket manager initialized")

    async def initialize(self) -> None:
        """Initialize Redis connection and start background tasks.

        Raises:
            Exception: If Redis connection fails
        """
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL, decode_responses=True
            )
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe(self.channel_name)

            self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
            self.pubsub_task = asyncio.create_task(self._pubsub_listener())

            logger.info(
                "WebSocket manager initialized with Redis",
                extra={"channel": self.channel_name},
            )
        except Exception as exc:
            logger.error(
                "Failed to initialize WebSocket manager",
                extra={"error": str(exc)},
                exc_info=True,
            )
            raise

    async def shutdown(self) -> None:
        """Shutdown manager and cleanup resources."""
        try:
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass

            if self.pubsub_task:
                self.pubsub_task.cancel()
                try:
                    await self.pubsub_task
                except asyncio.CancelledError:
                    pass

            if self.pubsub:
                await self.pubsub.unsubscribe(self.channel_name)
                await self.pubsub.close()

            if self.redis:
                await self.redis.close()

            for connection_id in list(self.connections.keys()):
                await self.disconnect(connection_id)

            logger.info("WebSocket manager shutdown completed")
        except Exception as exc:
            logger.error(
                "Error during WebSocket manager shutdown",
                extra={"error": str(exc)},
                exc_info=True,
            )

    async def connect(self, connection: WebSocketConnection) -> None:
        """Register a new WebSocket connection.

        Args:
            connection: WebSocketConnection instance to register
        """
        try:
            await connection.accept()

            self.connections[connection.connection_id] = connection

            if connection.user_id not in self.user_connections:
                self.user_connections[connection.user_id] = set()
            self.user_connections[connection.user_id].add(connection.connection_id)

            logger.info(
                "WebSocket connection registered",
                extra={
                    "user_id": str(connection.user_id),
                    "connection_id": connection.connection_id,
                    "total_connections": len(self.connections),
                    "user_connections": len(
                        self.user_connections.get(connection.user_id, set())
                    ),
                },
            )

            await self._send_connection_event(connection, "connected")
        except Exception as exc:
            logger.error(
                "Failed to register WebSocket connection",
                extra={
                    "user_id": str(connection.user_id),
                    "connection_id": connection.connection_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

    async def disconnect(self, connection_id: str, code: int = 1000, reason: str = "Normal closure") -> None:
        """Disconnect and remove a WebSocket connection.

        Args:
            connection_id: Connection identifier
            code: WebSocket close code
            reason: Close reason message
        """
        connection = self.connections.get(connection_id)
        if not connection:
            logger.warning(
                "Attempted to disconnect non-existent connection",
                extra={"connection_id": connection_id},
            )
            return

        try:
            await self._send_connection_event(connection, "disconnected")

            if connection.user_id in self.user_connections:
                self.user_connections[connection.user_id].discard(connection_id)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]

            del self.connections[connection_id]

            await connection.close(code=code, reason=reason)

            logger.info(
                "WebSocket connection disconnected",
                extra={
                    "user_id": str(connection.user_id),
                    "connection_id": connection_id,
                    "code": code,
                    "reason": reason,
                    "total_connections": len(self.connections),
                },
            )
        except Exception as exc:
            logger.error(
                "Error during WebSocket disconnection",
                extra={
                    "connection_id": connection_id,
                    "error": str(exc),
                },
                exc_info=True,
            )

    async def send_to_connection(
        self, connection_id: str, message: Dict[str, Any]
    ) -> bool:
        """Send message to a specific connection.

        Args:
            connection_id: Target connection identifier
            message: Message data to send

        Returns:
            True if sent successfully, False otherwise
        """
        connection = self.connections.get(connection_id)
        if not connection or not connection.is_connected():
            logger.warning(
                "Connection not found or not connected",
                extra={"connection_id": connection_id},
            )
            return False

        try:
            await connection.send_json(message)
            return True
        except Exception as exc:
            logger.error(
                "Failed to send message to connection",
                extra={
                    "connection_id": connection_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
            return False

    async def send_to_user(self, user_id: UUID, message: Dict[str, Any]) -> int:
        """Send message to all connections of a specific user.

        Args:
            user_id: Target user UUID
            message: Message data to send

        Returns:
            Number of connections message was sent to
        """
        connection_ids = self.user_connections.get(user_id, set())
        sent_count = 0

        for connection_id in connection_ids:
            if await self.send_to_connection(connection_id, message):
                sent_count += 1

        logger.debug(
            "Message sent to user connections",
            extra={
                "user_id": str(user_id),
                "sent_count": sent_count,
                "total_user_connections": len(connection_ids),
            },
        )

        return sent_count

    async def broadcast(
        self, message: Dict[str, Any], exclude_connection_id: Optional[str] = None
    ) -> int:
        """Broadcast message to all connections.

        Args:
            message: Message data to send
            exclude_connection_id: Optional connection ID to exclude from broadcast

        Returns:
            Number of connections message was sent to
        """
        sent_count = 0

        for connection_id, connection in self.connections.items():
            if connection_id == exclude_connection_id:
                continue

            if await self.send_to_connection(connection_id, message):
                sent_count += 1

        logger.info(
            "Message broadcasted",
            extra={
                "sent_count": sent_count,
                "total_connections": len(self.connections),
                "excluded_connection": exclude_connection_id,
            },
        )

        return sent_count

    async def publish_message(self, message: Dict[str, Any]) -> None:
        """Publish message to Redis pub/sub for multi-instance broadcasting.

        Args:
            message: Message data to publish

        Raises:
            Exception: If Redis publish fails
        """
        if not self.redis:
            logger.warning("Redis not initialized, cannot publish message")
            return

        try:
            message_json = json.dumps(message)
            await self.redis.publish(self.channel_name, message_json)
            logger.debug(
                "Message published to Redis",
                extra={
                    "channel": self.channel_name,
                    "message_type": message.get("type"),
                },
            )
        except Exception as exc:
            logger.error(
                "Failed to publish message to Redis",
                extra={
                    "channel": self.channel_name,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

    async def _pubsub_listener(self) -> None:
        """Background task to listen for Redis pub/sub messages."""
        if not self.pubsub:
            logger.error("Pub/sub not initialized")
            return

        logger.info("Redis pub/sub listener started")

        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await self.broadcast(data)
                    except json.JSONDecodeError as exc:
                        logger.error(
                            "Failed to decode pub/sub message",
                            extra={"error": str(exc)},
                        )
                    except Exception as exc:
                        logger.error(
                            "Error processing pub/sub message",
                            extra={"error": str(exc)},
                            exc_info=True,
                        )
        except asyncio.CancelledError:
            logger.info("Redis pub/sub listener cancelled")
        except Exception as exc:
            logger.error(
                "Redis pub/sub listener error",
                extra={"error": str(exc)},
                exc_info=True,
            )

    async def _heartbeat_monitor(self) -> None:
        """Background task to monitor connection heartbeats."""
        logger.info("Heartbeat monitor started")
        heartbeat_timeout = 60  # seconds

        try:
            while True:
                await asyncio.sleep(30)

                disconnected_ids: List[str] = []
                for connection_id, connection in self.connections.items():
                    time_since_ping = connection.get_time_since_last_ping()
                    if time_since_ping > heartbeat_timeout:
                        logger.warning(
                            "Connection heartbeat timeout",
                            extra={
                                "connection_id": connection_id,
                                "user_id": str(connection.user_id),
                                "time_since_ping": time_since_ping,
                            },
                        )
                        disconnected_ids.append(connection_id)

                for connection_id in disconnected_ids:
                    await self.disconnect(connection_id, code=1001, reason="Heartbeat timeout")

        except asyncio.CancelledError:
            logger.info("Heartbeat monitor cancelled")
        except Exception as exc:
            logger.error(
                "Heartbeat monitor error",
                extra={"error": str(exc)},
                exc_info=True,
            )

    async def _send_connection_event(
        self, connection: WebSocketConnection, event_type: str
    ) -> None:
        """Send connection event message.

        Args:
            connection: WebSocketConnection instance
            event_type: Event type (connected/disconnected)
        """
        try:
            message = {
                "type": "connection",
                "event": event_type,
                "user_id": str(connection.user_id),
                "connection_id": connection.connection_id,
                "timestamp": connection.connection_time.isoformat(),
            }
            await self.publish_message(message)
        except Exception as exc:
            logger.error(
                "Failed to send connection event",
                extra={
                    "event_type": event_type,
                    "connection_id": connection.connection_id,
                    "error": str(exc),
                },
                exc_info=True,
            )

    def get_connection_count(self) -> int:
        """Get total number of active connections.

        Returns:
            Number of active connections
        """
        return len(self.connections)

    def get_user_connection_count(self, user_id: UUID) -> int:
        """Get number of connections for a specific user.

        Args:
            user_id: User UUID

        Returns:
            Number of connections for the user
        """
        return len(self.user_connections.get(user_id, set()))

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics.

        Returns:
            Dictionary with manager statistics
        """
        return {
            "total_connections": self.get_connection_count(),
            "total_users": len(self.user_connections),
            "average_connections_per_user": (
                self.get_connection_count() / len(self.user_connections)
                if self.user_connections
                else 0
            ),
            "channel_name": self.channel_name,
        }
