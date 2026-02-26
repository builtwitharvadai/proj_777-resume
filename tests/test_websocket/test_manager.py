"""Unit tests for WebSocket connection manager."""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

import pytest

from src.websocket.connection import WebSocketConnection
from src.websocket.manager import WebSocketManager


class MockWebSocket:
    """Mock WebSocket for testing."""

    def __init__(self) -> None:
        """Initialize mock WebSocket."""
        self.accepted = False
        self.closed = False
        self.sent_messages: list = []
        self.receive_queue: asyncio.Queue = asyncio.Queue()

    async def accept(self) -> None:
        """Mock accept method."""
        self.accepted = True

    async def send_json(self, data: Dict[str, Any]) -> None:
        """Mock send_json method."""
        self.sent_messages.append(data)

    async def send_text(self, message: str) -> None:
        """Mock send_text method."""
        self.sent_messages.append({"text": message})

    async def receive_json(self) -> Dict[str, Any]:
        """Mock receive_json method."""
        return await self.receive_queue.get()

    async def receive_text(self) -> str:
        """Mock receive_text method."""
        data = await self.receive_queue.get()
        return json.dumps(data) if isinstance(data, dict) else str(data)

    async def close(self, code: int = 1000, reason: str = "Normal closure") -> None:
        """Mock close method."""
        self.closed = True


class TestWebSocketManager:
    """Test suite for WebSocketManager."""

    @pytest.mark.asyncio
    async def test_manager_initialization(self) -> None:
        """Test WebSocket manager initialization."""
        manager = WebSocketManager(channel_name="test_channel")

        assert manager.channel_name == "test_channel"
        assert len(manager.connections) == 0
        assert len(manager.user_connections) == 0
        assert manager.redis is None
        assert manager.pubsub is None

    @pytest.mark.asyncio
    async def test_manager_initialize_with_redis(self) -> None:
        """Test manager initialization with Redis connection."""
        manager = WebSocketManager()

        with patch("redis.asyncio.from_url") as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_pubsub = AsyncMock()
            mock_redis_instance.pubsub.return_value = mock_pubsub
            mock_redis.return_value = mock_redis_instance

            await manager.initialize()

            assert manager.redis is not None
            assert manager.pubsub is not None
            assert manager.heartbeat_task is not None
            assert manager.pubsub_task is not None

            await manager.shutdown()

    @pytest.mark.asyncio
    async def test_connect_new_connection(self) -> None:
        """Test connecting a new WebSocket connection."""
        manager = WebSocketManager()
        user_id = uuid4()
        connection_id = "test_connection_1"
        mock_websocket = MockWebSocket()

        connection = WebSocketConnection(
            websocket=mock_websocket,
            user_id=user_id,
            connection_id=connection_id,
        )

        with patch.object(manager, "_send_connection_event", new=AsyncMock()):
            await manager.connect(connection)

        assert connection_id in manager.connections
        assert user_id in manager.user_connections
        assert connection_id in manager.user_connections[user_id]
        assert mock_websocket.accepted is True

    @pytest.mark.asyncio
    async def test_connect_multiple_connections_same_user(self) -> None:
        """Test connecting multiple connections for same user."""
        manager = WebSocketManager()
        user_id = uuid4()
        connection_id_1 = "test_connection_1"
        connection_id_2 = "test_connection_2"

        mock_websocket_1 = MockWebSocket()
        mock_websocket_2 = MockWebSocket()

        connection_1 = WebSocketConnection(
            websocket=mock_websocket_1,
            user_id=user_id,
            connection_id=connection_id_1,
        )

        connection_2 = WebSocketConnection(
            websocket=mock_websocket_2,
            user_id=user_id,
            connection_id=connection_id_2,
        )

        with patch.object(manager, "_send_connection_event", new=AsyncMock()):
            await manager.connect(connection_1)
            await manager.connect(connection_2)

        assert len(manager.connections) == 2
        assert len(manager.user_connections[user_id]) == 2
        assert connection_id_1 in manager.user_connections[user_id]
        assert connection_id_2 in manager.user_connections[user_id]

    @pytest.mark.asyncio
    async def test_disconnect_connection(self) -> None:
        """Test disconnecting a WebSocket connection."""
        manager = WebSocketManager()
        user_id = uuid4()
        connection_id = "test_connection_1"
        mock_websocket = MockWebSocket()

        connection = WebSocketConnection(
            websocket=mock_websocket,
            user_id=user_id,
            connection_id=connection_id,
        )

        with patch.object(manager, "_send_connection_event", new=AsyncMock()):
            await manager.connect(connection)
            assert connection_id in manager.connections

            await manager.disconnect(connection_id)

        assert connection_id not in manager.connections
        assert user_id not in manager.user_connections
        assert mock_websocket.closed is True

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_connection(self) -> None:
        """Test disconnecting a non-existent connection."""
        manager = WebSocketManager()

        await manager.disconnect("nonexistent_connection")

        assert len(manager.connections) == 0

    @pytest.mark.asyncio
    async def test_send_to_connection(self) -> None:
        """Test sending message to specific connection."""
        manager = WebSocketManager()
        user_id = uuid4()
        connection_id = "test_connection_1"
        mock_websocket = MockWebSocket()

        connection = WebSocketConnection(
            websocket=mock_websocket,
            user_id=user_id,
            connection_id=connection_id,
        )

        with patch.object(manager, "_send_connection_event", new=AsyncMock()):
            await manager.connect(connection)

        message = {"type": "test", "content": "Hello"}
        result = await manager.send_to_connection(connection_id, message)

        assert result is True
        assert len(mock_websocket.sent_messages) == 1
        assert mock_websocket.sent_messages[0] == message

    @pytest.mark.asyncio
    async def test_send_to_user(self) -> None:
        """Test sending message to all user connections."""
        manager = WebSocketManager()
        user_id = uuid4()
        connection_id_1 = "test_connection_1"
        connection_id_2 = "test_connection_2"

        mock_websocket_1 = MockWebSocket()
        mock_websocket_2 = MockWebSocket()

        connection_1 = WebSocketConnection(
            websocket=mock_websocket_1,
            user_id=user_id,
            connection_id=connection_id_1,
        )

        connection_2 = WebSocketConnection(
            websocket=mock_websocket_2,
            user_id=user_id,
            connection_id=connection_id_2,
        )

        with patch.object(manager, "_send_connection_event", new=AsyncMock()):
            await manager.connect(connection_1)
            await manager.connect(connection_2)

        message = {"type": "test", "content": "Broadcast to user"}
        sent_count = await manager.send_to_user(user_id, message)

        assert sent_count == 2
        assert mock_websocket_1.sent_messages[0] == message
        assert mock_websocket_2.sent_messages[0] == message

    @pytest.mark.asyncio
    async def test_broadcast_to_all(self) -> None:
        """Test broadcasting message to all connections."""
        manager = WebSocketManager()
        user_id_1 = uuid4()
        user_id_2 = uuid4()

        connection_id_1 = "test_connection_1"
        connection_id_2 = "test_connection_2"

        mock_websocket_1 = MockWebSocket()
        mock_websocket_2 = MockWebSocket()

        connection_1 = WebSocketConnection(
            websocket=mock_websocket_1,
            user_id=user_id_1,
            connection_id=connection_id_1,
        )

        connection_2 = WebSocketConnection(
            websocket=mock_websocket_2,
            user_id=user_id_2,
            connection_id=connection_id_2,
        )

        with patch.object(manager, "_send_connection_event", new=AsyncMock()):
            await manager.connect(connection_1)
            await manager.connect(connection_2)

        message = {"type": "test", "content": "Broadcast to all"}
        sent_count = await manager.broadcast(message)

        assert sent_count == 2
        assert mock_websocket_1.sent_messages[0] == message
        assert mock_websocket_2.sent_messages[0] == message

    @pytest.mark.asyncio
    async def test_broadcast_exclude_connection(self) -> None:
        """Test broadcasting with excluded connection."""
        manager = WebSocketManager()
        user_id_1 = uuid4()
        user_id_2 = uuid4()

        connection_id_1 = "test_connection_1"
        connection_id_2 = "test_connection_2"

        mock_websocket_1 = MockWebSocket()
        mock_websocket_2 = MockWebSocket()

        connection_1 = WebSocketConnection(
            websocket=mock_websocket_1,
            user_id=user_id_1,
            connection_id=connection_id_1,
        )

        connection_2 = WebSocketConnection(
            websocket=mock_websocket_2,
            user_id=user_id_2,
            connection_id=connection_id_2,
        )

        with patch.object(manager, "_send_connection_event", new=AsyncMock()):
            await manager.connect(connection_1)
            await manager.connect(connection_2)

        message = {"type": "test", "content": "Broadcast excluding one"}
        sent_count = await manager.broadcast(message, exclude_connection_id=connection_id_1)

        assert sent_count == 1
        assert len(mock_websocket_1.sent_messages) == 0
        assert mock_websocket_2.sent_messages[0] == message

    @pytest.mark.asyncio
    async def test_publish_message(self) -> None:
        """Test publishing message to Redis pub/sub."""
        manager = WebSocketManager()

        mock_redis = AsyncMock()
        manager.redis = mock_redis

        message = {"type": "test", "content": "Redis pub/sub test"}
        await manager.publish_message(message)

        mock_redis.publish.assert_called_once()
        call_args = mock_redis.publish.call_args
        assert call_args[0][0] == manager.channel_name
        assert json.loads(call_args[0][1]) == message

    @pytest.mark.asyncio
    async def test_get_connection_count(self) -> None:
        """Test getting total connection count."""
        manager = WebSocketManager()
        assert manager.get_connection_count() == 0

        user_id = uuid4()
        connection_id = "test_connection_1"
        mock_websocket = MockWebSocket()

        connection = WebSocketConnection(
            websocket=mock_websocket,
            user_id=user_id,
            connection_id=connection_id,
        )

        with patch.object(manager, "_send_connection_event", new=AsyncMock()):
            await manager.connect(connection)

        assert manager.get_connection_count() == 1

    @pytest.mark.asyncio
    async def test_get_user_connection_count(self) -> None:
        """Test getting connection count for specific user."""
        manager = WebSocketManager()
        user_id = uuid4()

        assert manager.get_user_connection_count(user_id) == 0

        connection_id_1 = "test_connection_1"
        connection_id_2 = "test_connection_2"

        mock_websocket_1 = MockWebSocket()
        mock_websocket_2 = MockWebSocket()

        connection_1 = WebSocketConnection(
            websocket=mock_websocket_1,
            user_id=user_id,
            connection_id=connection_id_1,
        )

        connection_2 = WebSocketConnection(
            websocket=mock_websocket_2,
            user_id=user_id,
            connection_id=connection_id_2,
        )

        with patch.object(manager, "_send_connection_event", new=AsyncMock()):
            await manager.connect(connection_1)
            await manager.connect(connection_2)

        assert manager.get_user_connection_count(user_id) == 2

    @pytest.mark.asyncio
    async def test_get_stats(self) -> None:
        """Test getting manager statistics."""
        manager = WebSocketManager()
        user_id_1 = uuid4()
        user_id_2 = uuid4()

        connection_id_1 = "test_connection_1"
        connection_id_2 = "test_connection_2"
        connection_id_3 = "test_connection_3"

        mock_websocket_1 = MockWebSocket()
        mock_websocket_2 = MockWebSocket()
        mock_websocket_3 = MockWebSocket()

        connections = [
            WebSocketConnection(mock_websocket_1, user_id_1, connection_id_1),
            WebSocketConnection(mock_websocket_2, user_id_1, connection_id_2),
            WebSocketConnection(mock_websocket_3, user_id_2, connection_id_3),
        ]

        with patch.object(manager, "_send_connection_event", new=AsyncMock()):
            for conn in connections:
                await manager.connect(conn)

        stats = manager.get_stats()

        assert stats["total_connections"] == 3
        assert stats["total_users"] == 2
        assert stats["average_connections_per_user"] == 1.5
        assert stats["channel_name"] == manager.channel_name

    @pytest.mark.asyncio
    async def test_heartbeat_timeout_disconnect(self) -> None:
        """Test heartbeat timeout triggers disconnection."""
        manager = WebSocketManager()
        user_id = uuid4()
        connection_id = "test_connection_1"
        mock_websocket = MockWebSocket()

        connection = WebSocketConnection(
            websocket=mock_websocket,
            user_id=user_id,
            connection_id=connection_id,
        )

        with patch.object(manager, "_send_connection_event", new=AsyncMock()):
            await manager.connect(connection)

        with patch.object(connection, "get_time_since_last_ping", return_value=70.0):
            with patch.object(manager, "disconnect", new=AsyncMock()) as mock_disconnect:
                heartbeat_task = asyncio.create_task(manager._heartbeat_monitor())

                await asyncio.sleep(0.1)

                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

    @pytest.mark.asyncio
    async def test_shutdown_cleanup(self) -> None:
        """Test manager shutdown cleans up resources."""
        manager = WebSocketManager()

        with patch("redis.asyncio.from_url") as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_pubsub = AsyncMock()
            mock_redis_instance.pubsub.return_value = mock_pubsub
            mock_redis.return_value = mock_redis_instance

            await manager.initialize()

            user_id = uuid4()
            connection_id = "test_connection_1"
            mock_websocket = MockWebSocket()

            connection = WebSocketConnection(
                websocket=mock_websocket,
                user_id=user_id,
                connection_id=connection_id,
            )

            with patch.object(manager, "_send_connection_event", new=AsyncMock()):
                await manager.connect(connection)

            assert len(manager.connections) == 1

            await manager.shutdown()

            assert len(manager.connections) == 0
            assert mock_websocket.closed is True
            mock_pubsub.unsubscribe.assert_called_once()
            mock_pubsub.close.assert_called_once()
            mock_redis_instance.close.assert_called_once()
