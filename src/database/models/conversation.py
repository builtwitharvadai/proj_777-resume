"""Conversation model for Q&A threading and categorization."""

import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import relationship

from src.database.base import BaseModel


class ConversationCategory(str, enum.Enum):
    """Enumeration for conversation categories."""

    RESUME_HELP = "resume_help"
    CAREER_ADVICE = "career_advice"
    INTERVIEW_PREP = "interview_prep"
    JOB_SEARCH = "job_search"


class Conversation(BaseModel):
    """Conversation model with threading, categorization, and metadata.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        user_id: Foreign key to users table
        title: Conversation title
        category: Category enum for conversation type
        tags: JSON array of tags for searchability
        is_active: Flag indicating if conversation is active
        created_at: Timestamp of creation (inherited from BaseModel)
        updated_at: Timestamp of last update (inherited from BaseModel)
        last_message_at: Timestamp of last message in conversation
    """

    __tablename__ = "conversations"

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(
        String(500),
        nullable=False,
        index=True,
    )

    category = Column(
        Enum(ConversationCategory, name="conversation_category"),
        nullable=False,
        index=True,
    )

    tags = Column(
        JSON,
        nullable=False,
        default=list,
        server_default="[]",
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    last_message_at = Column(
        DateTime,
        nullable=True,
        index=True,
    )

    user = relationship("User", backref="conversations")

    __table_args__ = (
        Index("ix_conversations_user_category", "user_id", "category"),
        Index("ix_conversations_user_active", "user_id", "is_active"),
        Index(
            "ix_conversations_user_last_message",
            "user_id",
            "last_message_at",
        ),
    )

    def __repr__(self) -> str:
        """String representation of Conversation model.

        Returns:
            str: String representation showing id, title, and category
        """
        return (
            f"<Conversation(id={self.id}, title={self.title!r}, "
            f"category={self.category.value})>"
        )
