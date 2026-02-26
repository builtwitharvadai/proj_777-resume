"""WebSocket endpoint for real-time Q&A messaging."""

import asyncio
import logging
import uuid
from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from src.websocket.auth import authenticate_websocket, validate_websocket_message
from src.websocket.connection import WebSocketConnection
from src.websocket.manager import WebSocketManager
from src.websocket.models import HeartbeatMessage, MessageType

logger = logging.getLogger(__name__)

router = APIRouter()

ws_manager = WebSocketManager()


@router.on_event("startup")
async def startup_websocket() -> None:
    """Initialize WebSocket manager on startup."""
    try:
        await ws_manager.initialize()
        logger.info("WebSocket manager started")
    except Exception as exc:
        logger.error(
            "Failed to start WebSocket manager",
            extra={"error": str(exc)},
            exc_info=True,
        )


@router.on_event("shutdown")
async def shutdown_websocket() -> None:
    """Shutdown WebSocket manager on application shutdown."""
    try:
        await ws_manager.shutdown()
        logger.info("WebSocket manager stopped")
    except Exception as exc:
        logger.error(
            "Error during WebSocket manager shutdown",
            extra={"error": str(exc)},
            exc_info=True,
        )


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time messaging.

    Args:
        websocket: WebSocket connection instance

    Raises:
        WebSocketDisconnect: When client disconnects
    """
    connection_id = str(uuid.uuid4())
    connection: WebSocketConnection = None

    try:
        user = await authenticate_websocket(websocket)

        connection = WebSocketConnection(
            websocket=websocket,
            user_id=user.id,
            connection_id=connection_id,
            metadata={"email": user.email, "email_verified": user.email_verified},
        )

        await ws_manager.connect(connection)

        logger.info(
            "WebSocket connection established",
            extra={
                "user_id": str(user.id),
                "connection_id": connection_id,
                "email": user.email,
            },
        )

        await connection.send_json(
            {
                "type": MessageType.CONNECTION.value,
                "event": "connected",
                "connection_id": connection_id,
                "user_id": str(user.id),
            }
        )

        heartbeat_task = asyncio.create_task(
            _send_heartbeats(connection)
        )

        try:
            while True:
                data = await connection.receive_json()

                message_type = data.get("type")
                logger.debug(
                    "WebSocket message received",
                    extra={
                        "user_id": str(user.id),
                        "connection_id": connection_id,
                        "message_type": message_type,
                    },
                )

                if message_type == MessageType.HEARTBEAT.value:
                    connection.update_ping()
                    await connection.send_json(
                        {
                            "type": MessageType.HEARTBEAT.value,
                            "ping": False,
                            "timestamp": HeartbeatMessage().timestamp.isoformat(),
                        }
                    )
                    continue

                if not validate_websocket_message(data, user.id):
                    logger.warning(
                        "Invalid WebSocket message",
                        extra={
                            "user_id": str(user.id),
                            "connection_id": connection_id,
                        },
                    )
                    await connection.send_json(
                        {
                            "type": MessageType.ERROR.value,
                            "error": "Invalid message format",
                        }
                    )
                    continue

                await _handle_message(connection, data)

        except WebSocketDisconnect:
            logger.info(
                "WebSocket client disconnected",
                extra={
                    "user_id": str(user.id),
                    "connection_id": connection_id,
                },
            )
        except asyncio.CancelledError:
            logger.info(
                "WebSocket connection cancelled",
                extra={
                    "user_id": str(user.id),
                    "connection_id": connection_id,
                },
            )
        except Exception as exc:
            logger.error(
                "WebSocket error",
                extra={
                    "user_id": str(user.id),
                    "connection_id": connection_id,
                    "error": str(exc),
                },
                exc_info=True,
            )
            try:
                await connection.send_json(
                    {
                        "type": MessageType.ERROR.value,
                        "error": "Internal server error",
                    }
                )
            except Exception:
                pass
        finally:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

    except Exception as exc:
        logger.error(
            "WebSocket connection error",
            extra={
                "connection_id": connection_id,
                "error": str(exc),
            },
            exc_info=True,
        )
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass
    finally:
        if connection:
            await ws_manager.disconnect(connection_id, code=1000, reason="Connection closed")


async def _send_heartbeats(connection: WebSocketConnection) -> None:
    """Send periodic heartbeat messages to keep connection alive.

    Args:
        connection: WebSocketConnection instance
    """
    try:
        while True:
            await asyncio.sleep(30)

            if not connection.is_connected():
                logger.debug(
                    "Connection not active, stopping heartbeats",
                    extra={"connection_id": connection.connection_id},
                )
                break

            try:
                heartbeat = HeartbeatMessage(ping=True)
                await connection.send_json(
                    {
                        "type": heartbeat.type.value,
                        "ping": heartbeat.ping,
                        "timestamp": heartbeat.timestamp.isoformat(),
                    }
                )
            except Exception as exc:
                logger.error(
                    "Failed to send heartbeat",
                    extra={
                        "connection_id": connection.connection_id,
                        "error": str(exc),
                    },
                )
                break

    except asyncio.CancelledError:
        logger.debug(
            "Heartbeat task cancelled",
            extra={"connection_id": connection.connection_id},
        )
    except Exception as exc:
        logger.error(
            "Heartbeat task error",
            extra={
                "connection_id": connection.connection_id,
                "error": str(exc),
            },
            exc_info=True,
        )


async def _handle_message(connection: WebSocketConnection, data: Dict[str, Any]) -> None:
    """Handle incoming WebSocket message.

    Args:
        connection: WebSocketConnection instance
        data: Message data dictionary
    """
    message_type = data.get("type")

    try:
        if message_type == MessageType.CHAT.value:
            await ws_manager.publish_message(data)
            logger.info(
                "Chat message published",
                extra={
                    "user_id": str(connection.user_id),
                    "connection_id": connection.connection_id,
                },
            )

        elif message_type == MessageType.TYPING.value:
            await ws_manager.publish_message(data)
            logger.debug(
                "Typing indicator published",
                extra={
                    "user_id": str(connection.user_id),
                    "connection_id": connection.connection_id,
                },
            )

        else:
            logger.warning(
                "Unknown message type",
                extra={
                    "user_id": str(connection.user_id),
                    "connection_id": connection.connection_id,
                    "message_type": message_type,
                },
            )
            await connection.send_json(
                {
                    "type": MessageType.ERROR.value,
                    "error": f"Unknown message type: {message_type}",
                }
            )

    except Exception as exc:
        logger.error(
            "Error handling message",
            extra={
                "user_id": str(connection.user_id),
                "connection_id": connection.connection_id,
                "message_type": message_type,
                "error": str(exc),
            },
            exc_info=True,
        )
        await connection.send_json(
            {
                "type": MessageType.ERROR.value,
                "error": "Failed to process message",
            }
        )
