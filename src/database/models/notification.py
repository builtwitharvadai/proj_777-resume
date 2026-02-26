"""Notification model for in-app notifications."""

from sqlalchemy import Boolean, Column, ForeignKey, Index, JSON, String, Text

from src.database.base import BaseModel


class Notification(BaseModel):
    """Notification model for tracking user notifications.

    Attributes:
        id: UUID primary key (inherited from BaseModel)
        user_id: Foreign key to users table
        type: Notification type identifier
        title: Notification title
        message: Notification message content
        data: JSON field for additional notification data
        read: Flag indicating if notification has been read
        created_at: Timestamp of creation (inherited from BaseModel)
        updated_at: Timestamp of last update (inherited from BaseModel)
    """

    __tablename__ = "notifications"

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    data = Column(
        JSON,
        default=dict,
        nullable=False,
    )

    read = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index("ix_notifications_user_id_read", "user_id", "read"),
    )

    def __repr__(self) -> str:
        """String representation of Notification model.

        Returns:
            str: String representation showing id, user_id, type, and read status
        """
        return (
            f"<Notification(id={self.id}, user_id={self.user_id}, "
            f"type={self.type}, read={self.read})>"
        )
