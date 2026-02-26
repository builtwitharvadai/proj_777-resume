"""Pydantic schemas for Q&A API requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class QuestionRequest(BaseModel):
    """Request schema for asking a question.

    Attributes:
        question: User's question text
        conversation_id: Optional ID of existing conversation to continue
        category: Optional conversation category
        metadata: Optional additional metadata
    """

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User's question text",
    )
    conversation_id: Optional[UUID] = Field(
        None,
        description="Optional conversation ID to continue existing thread",
    )
    category: Optional[str] = Field(
        None,
        description="Category for conversation (resume_help, career_advice, etc)",
    )
    metadata: Optional[dict] = Field(
        default_factory=dict,
        description="Optional metadata for the question",
    )

    @field_validator("question")
    @classmethod
    def validate_question_not_empty(cls, v: str) -> str:
        """Validate that question is not just whitespace.

        Args:
            v: Question text

        Returns:
            str: Validated question text

        Raises:
            ValueError: If question is empty or only whitespace
        """
        if not v or not v.strip():
            raise ValueError("Question cannot be empty or only whitespace")
        return v.strip()


class MessageResponse(BaseModel):
    """Response schema for a single message.

    Attributes:
        id: Message UUID
        conversation_id: Conversation UUID
        sender_type: Type of sender (user or ai)
        content: Message content
        metadata: Message metadata
        created_at: Timestamp when message was created
    """

    id: UUID
    conversation_id: UUID
    sender_type: str
    content: str
    metadata: dict
    created_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ConversationResponse(BaseModel):
    """Response schema for conversation with messages.

    Attributes:
        id: Conversation UUID
        user_id: User UUID
        title: Conversation title
        category: Conversation category
        tags: List of tags
        is_active: Whether conversation is active
        last_message_at: Timestamp of last message
        created_at: Timestamp when conversation was created
        updated_at: Timestamp when conversation was last updated
        messages: List of messages in conversation
    """

    id: UUID
    user_id: str
    title: str
    category: str
    tags: List[str]
    is_active: bool
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ConversationListResponse(BaseModel):
    """Response schema for list of conversations.

    Attributes:
        conversations: List of conversations
        total: Total count of conversations
        offset: Current offset for pagination
        limit: Current limit for pagination
    """

    conversations: List[ConversationResponse]
    total: int
    offset: int
    limit: int


class SearchRequest(BaseModel):
    """Request schema for searching messages.

    Attributes:
        query: Search query text
        conversation_id: Optional conversation ID to limit search
        limit: Maximum number of results
        offset: Offset for pagination
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query text",
    )
    conversation_id: Optional[UUID] = Field(
        None,
        description="Optional conversation ID to limit search",
    )
    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of results to return",
    )
    offset: int = Field(
        0,
        ge=0,
        description="Offset for pagination",
    )

    @field_validator("query")
    @classmethod
    def validate_query_not_empty(cls, v: str) -> str:
        """Validate that search query is not just whitespace.

        Args:
            v: Search query text

        Returns:
            str: Validated query text

        Raises:
            ValueError: If query is empty or only whitespace
        """
        if not v or not v.strip():
            raise ValueError("Search query cannot be empty or only whitespace")
        return v.strip()


class MessageRatingRequest(BaseModel):
    """Request schema for rating a message.

    Attributes:
        rating: Rating value (1-5)
        feedback_text: Optional feedback text
    """

    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Rating value from 1 to 5",
    )
    feedback_text: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional feedback text",
    )
