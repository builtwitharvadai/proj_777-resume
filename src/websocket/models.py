"""Pydantic models for WebSocket message types and events."""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types."""

    HEARTBEAT = "heartbeat"
    CONNECTION = "connection"
    CHAT = "chat"
    TYPING = "typing"
    ERROR = "error"


class ConnectionEventType(str, Enum):
    """WebSocket connection event types."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PING = "ping"
    PONG = "pong"


class WebSocketMessage(BaseModel):
    """Base WebSocket message model.

    Attributes:
        type: Message type
        timestamp: Message timestamp
        data: Message payload data
    """

    type: MessageType = Field(..., description="Message type")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Message timestamp"
    )
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate message data is a dictionary.

        Args:
            v: Data to validate

        Returns:
            Validated data

        Raises:
            ValueError: If data is not a dictionary
        """
        if not isinstance(v, dict):
            logger.warning("Invalid data type, expected dict")
            raise ValueError("Message data must be a dictionary")
        return v

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ConnectionEvent(BaseModel):
    """WebSocket connection event model.

    Attributes:
        event_type: Connection event type
        user_id: User UUID
        connection_id: Connection identifier
        timestamp: Event timestamp
        metadata: Additional event metadata
    """

    event_type: ConnectionEventType = Field(..., description="Connection event type")
    user_id: UUID = Field(..., description="User UUID")
    connection_id: str = Field(..., description="Connection identifier")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Event metadata"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}


class HeartbeatMessage(BaseModel):
    """WebSocket heartbeat/ping-pong message model.

    Attributes:
        type: Message type (always 'heartbeat')
        timestamp: Heartbeat timestamp
        ping: True for ping, False for pong
    """

    type: MessageType = Field(default=MessageType.HEARTBEAT, description="Message type")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Heartbeat timestamp"
    )
    ping: bool = Field(True, description="True for ping, False for pong")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ChatMessage(BaseModel):
    """WebSocket chat message model.

    Attributes:
        type: Message type (always 'chat')
        user_id: Sender user UUID
        content: Message content
        conversation_id: Conversation UUID
        timestamp: Message timestamp
        metadata: Additional message metadata
    """

    type: MessageType = Field(default=MessageType.CHAT, description="Message type")
    user_id: UUID = Field(..., description="Sender user UUID")
    content: str = Field(..., min_length=1, description="Message content")
    conversation_id: Optional[UUID] = Field(None, description="Conversation UUID")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Message timestamp"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Message metadata"
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate message content is not empty.

        Args:
            v: Content to validate

        Returns:
            Validated content

        Raises:
            ValueError: If content is empty
        """
        if not v or not v.strip():
            logger.warning("Empty message content")
            raise ValueError("Message content cannot be empty")
        return v.strip()

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}


class TypingIndicator(BaseModel):
    """WebSocket typing indicator model.

    Attributes:
        type: Message type (always 'typing')
        user_id: User UUID who is typing
        conversation_id: Conversation UUID
        is_typing: True if user is typing, False if stopped
        timestamp: Indicator timestamp
    """

    type: MessageType = Field(default=MessageType.TYPING, description="Message type")
    user_id: UUID = Field(..., description="User UUID who is typing")
    conversation_id: UUID = Field(..., description="Conversation UUID")
    is_typing: bool = Field(..., description="Typing status")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Indicator timestamp"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)}
