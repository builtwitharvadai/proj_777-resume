"""Message model for Q&A exchanges with full-text search support."""

import enum
from sqlalchemy import Column, DDL, Enum, ForeignKey, Index, String, Text, event
from sqlalchemy.dialects.postgresql import JSON, TSVECTOR
from sqlalchemy.orm import relationship

from src.database.base import BaseModel


class SenderType(str, enum.Enum):
    """Enumeration for message sender types."""

    USER = "user"
    AI = "ai"


class Message(BaseModel):
    """Message model for Q&A exchanges with full-text search support.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        conversation_id: Foreign key to conversations table
        sender_type: Enum indicating if message is from user or AI
        content: Message text content
        search_vector: PostgreSQL tsvector for full-text search
        metadata: JSON field for additional message metadata
        created_at: Timestamp of creation (inherited from BaseModel)
        updated_at: Timestamp of last update (inherited from BaseModel)
    """

    __tablename__ = "messages"

    conversation_id = Column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sender_type = Column(
        Enum(SenderType, name="sender_type"),
        nullable=False,
        index=True,
    )

    content = Column(
        Text,
        nullable=False,
    )

    search_vector = Column(
        TSVECTOR,
        nullable=True,
    )

    metadata = Column(
        JSON,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    conversation = relationship("Conversation", backref="messages")

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
        Index(
            "ix_messages_search_vector",
            "search_vector",
            postgresql_using="gin",
        ),
        Index("ix_messages_sender_type_created", "sender_type", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation of Message model.

        Returns:
            str: String representation showing id, sender, and content preview
        """
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return (
            f"<Message(id={self.id}, sender={self.sender_type.value}, "
            f"content={content_preview!r})>"
        )


# Create trigger for automatic search_vector update
search_vector_trigger = DDL(
    """
    CREATE TRIGGER messages_search_vector_update
    BEFORE INSERT OR UPDATE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION
        tsvector_update_trigger(
            search_vector,
            'pg_catalog.english',
            content
        );
    """
)

# Register the trigger to be created after table creation
event.listen(
    Message.__table__,
    "after_create",
    search_vector_trigger.execute_if(dialect="postgresql"),
)
