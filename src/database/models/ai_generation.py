"""AI generation tracking model for AI service requests and usage monitoring."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Text

from src.database.base import BaseModel


class AIGeneration(BaseModel):
    """AI generation tracking model for monitoring AI API usage and costs.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        user_id: Foreign key to users table
        document_id: Foreign key to documents table (optional)
        generation_type: Type of generation (resume or cover_letter)
        prompt_tokens: Number of tokens used in the prompt
        completion_tokens: Number of tokens in the completion
        total_tokens: Total tokens used (prompt + completion)
        cost_usd: Cost in USD for this generation
        model_used: OpenAI model used (e.g., gpt-4)
        status: Generation status (pending, completed, failed)
        generated_content: The generated content text
        error_message: Error message if generation failed
        created_at: Timestamp of record creation (inherited from BaseModel)
        updated_at: Timestamp of last update (inherited from BaseModel)
    """

    __tablename__ = "ai_generations"

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    document_id = Column(
        String(36),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    generation_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    prompt_tokens = Column(
        Integer,
        nullable=False,
        default=0,
    )

    completion_tokens = Column(
        Integer,
        nullable=False,
        default=0,
    )

    total_tokens = Column(
        Integer,
        nullable=False,
        default=0,
    )

    cost_usd = Column(
        Numeric(10, 6),
        nullable=False,
        default=Decimal("0.000000"),
    )

    model_used = Column(
        String(50),
        nullable=False,
    )

    status = Column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )

    generated_content = Column(
        Text,
        nullable=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        Index("ix_ai_generations_user_id_created_at", "user_id", "created_at"),
        Index("ix_ai_generations_generation_type", "generation_type"),
        Index("ix_ai_generations_status", "status"),
        Index("ix_ai_generations_model_used", "model_used"),
    )

    def __repr__(self) -> str:
        """String representation of AIGeneration model.

        Returns:
            str: String representation showing generation type and user
        """
        return (
            f"<AIGeneration(id={self.id}, user_id={self.user_id}, "
            f"generation_type={self.generation_type}, status={self.status})>"
        )
