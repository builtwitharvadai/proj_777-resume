"""Message rating and feedback model for AI response quality tracking."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.database.base import BaseModel


class MessageRating(BaseModel):
    """Message rating and feedback model for AI response quality tracking.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        message_id: Foreign key to messages table
        user_id: Foreign key to users table
        rating: Integer rating from 1 to 5
        feedback_text: Optional text feedback from user
        helpful: Boolean indicating if message was helpful
        created_at: Timestamp of creation (inherited from BaseModel)
        updated_at: Timestamp of last update (inherited from BaseModel)
    """

    __tablename__ = "message_ratings"

    message_id = Column(
        String(36),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    rating = Column(
        Integer,
        nullable=False,
    )

    feedback_text = Column(
        Text,
        nullable=True,
    )

    helpful = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    message = relationship("Message", backref="ratings")
    user = relationship("User", backref="message_ratings")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_rating_range"),
        UniqueConstraint("message_id", "user_id", name="uq_message_user_rating"),
        Index("ix_message_ratings_message_rating", "message_id", "rating"),
        Index("ix_message_ratings_user_created", "user_id", "created_at"),
        Index("ix_message_ratings_helpful", "helpful"),
    )

    def __repr__(self) -> str:
        """String representation of MessageRating model.

        Returns:
            str: String representation showing id, rating, and helpful status
        """
        return (
            f"<MessageRating(id={self.id}, rating={self.rating}, "
            f"helpful={self.helpful})>"
        )
